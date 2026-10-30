import os,re,html,secrets,uuid,io
from pathlib import Path
from datetime import datetime,timedelta,timezone
import bcrypt,jwt,numpy as np
from PIL import Image,UnidentifiedImageError
from fastapi import FastAPI,UploadFile,File,Depends,Header,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel,Field
from database import DATA,SessionLocal,User,Note
app=FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_methods=['*'],allow_headers=['*'])
keyfile=DATA/'.jwt_secret'
if not keyfile.exists():keyfile.write_text(secrets.token_hex(32));keyfile.chmod(0o600)
SECRET=os.getenv('JWT_SECRET') or keyfile.read_text()
UPLOAD=DATA/'images';UPLOAD.mkdir(exist_ok=True)
SEARCH=os.getenv('SEARCH_BACKEND','keyword');encoder=None
class Credentials(BaseModel):
 username:str=Field(pattern=r'^[a-zA-Z0-9_]{3,40}$');password:str=Field(min_length=6,max_length=72)
def db_session():
 db=SessionLocal()
 try:yield db
 finally:db.close()
def current_user(token:str=Header(...),db=Depends(db_session)):
 try:
  name=jwt.decode(token,SECRET,algorithms=['HS256'])['sub'];u=db.query(User).filter_by(username=name).first()
  if not u:raise ValueError()
  return u
 except Exception:raise HTTPException(401,'다시 로그인해주세요.')
@app.get('/health/')
def health():return {'status':'ok','search_backend':SEARCH,'ocr_backend':os.getenv('OCR_BACKEND','tesseract')}
@app.post('/signup/')
def signup(c:Credentials,db=Depends(db_session)):
 if db.query(User).filter_by(username=c.username).first():raise HTTPException(409,'이미 사용 중인 아이디입니다.')
 u=User(username=c.username,hashed_password=bcrypt.hashpw(c.password.encode(),bcrypt.gensalt()).decode());db.add(u);db.commit();return {'username':c.username}
@app.post('/login/')
def login(c:Credentials,db=Depends(db_session)):
 u=db.query(User).filter_by(username=c.username).first()
 if not u or not bcrypt.checkpw(c.password.encode(),u.hashed_password.encode()):raise HTTPException(401,'아이디 또는 비밀번호를 확인해주세요.')
 return {'access_token':jwt.encode({'sub':u.username,'exp':datetime.now(timezone.utc)+timedelta(hours=12)},SECRET,algorithm='HS256')}
from ocr_runtime import extract, normalize_image
@app.post('/upload/')
async def upload(file:UploadFile=File(...),u=Depends(current_user),db=Depends(db_session)):
 data=await file.read(12*1024*1024+1)
 if len(data)>12*1024*1024:raise HTTPException(413,'12MB 이하 이미지를 사용해주세요.')
 try:
  im=Image.open(io.BytesIO(data));im.verify()
 except Exception:raise HTTPException(400,'이미지 파일을 확인해주세요.')
 try:text=extract(data)
 except Exception as e:
  import logging
  error_id = uuid.uuid4().hex[:8]
  logging.getLogger('uvicorn.error').exception('OCR_ERROR id=%s type=%s', error_id, type(e).__name__)
  message = 'OCR 처리에 실패했습니다.'
  if type(e).__name__ == 'TesseractNotFoundError':
   message = 'Tesseract 실행 파일을 찾지 못했습니다. 설치 경로를 확인해주세요.'
  elif 'timeout' in str(e).lower():
   message = 'OCR 처리 시간이 초과되었습니다. 이미지 크기를 줄여주세요.'
  raise HTTPException(503, f'{message} 오류 종류: {type(e).__name__}, 확인 번호: {error_id}. 서버 터미널의 OCR_ERROR 내용을 확인해주세요.') from e
 if not text.strip():raise HTTPException(422,'텍스트를 읽지 못했습니다. 더 선명한 이미지를 사용해주세요.')
 name=uuid.uuid4().hex+'.png';normalize_image(data).save(UPLOAD/name)
 path=f'images/{name}';db.add(Note(user_id=u.id,image_path=path,filename=file.filename,text=text));db.commit()
 return {'image_path':path,'preview':text.splitlines()[:3],'num_sentences':len(text.splitlines())}
@app.get('/my_images/')
def images(u=Depends(current_user),db=Depends(db_session)):return {'images':[n.image_path for n in db.query(Note).filter_by(user_id=u.id).order_by(Note.id.desc())]}
def owned(name,u,db):
 n=db.query(Note).filter_by(user_id=u.id,image_path='images/'+Path(name).name).first()
 if not n:raise HTTPException(404,'이미지를 찾을 수 없습니다.')
 return n
@app.get('/images/{name}')
def image(name:str,u=Depends(current_user),db=Depends(db_session)):
 owned(name,u,db);return FileResponse(UPLOAD/Path(name).name)
@app.delete('/delete_image/{name}')
def delete(name:str,u=Depends(current_user),db=Depends(db_session)):
 n=owned(name,u,db);(UPLOAD/Path(name).name).unlink(missing_ok=True);db.delete(n);db.commit();return {'message':'삭제 완료'}
@app.get('/semantic_search/')
def search(query:str,u=Depends(current_user),db=Depends(db_session)):
 global encoder
 query=query.strip()
 if not query:return []
 notes=db.query(Note).filter_by(user_id=u.id).all();rows=[(n,s.strip()) for n in notes for s in re.split(r'[\n.]',n.text) if len(s.strip())>1]
 if not rows:return []
 if SEARCH=='bge':
  from sentence_transformers import SentenceTransformer
  if encoder is None:encoder=SentenceTransformer('BAAI/bge-m3')
  vec=encoder.encode([query]+[s for n,s in rows],normalize_embeddings=True);scores=vec[1:]@vec[0];threshold=.45
 else:
  from sklearn.feature_extraction.text import TfidfVectorizer
  mat=TfidfVectorizer(analyzer='char',ngram_range=(1,4)).fit_transform([query]+[s for n,s in rows]);scores=(mat[1:]@mat[0].T).toarray().ravel();threshold=.04
  terms=query.casefold().split()
  scores=np.array([score if any(term in sentence.casefold() for term in terms) else 0 for score,(_,sentence) in zip(scores,rows)])
 grouped={}
 for idx in np.argsort(scores)[::-1][:10]:
  if scores[idx]<threshold:continue
  n,s=rows[idx];safe=html.escape(s);q=html.escape(query);highlighted=re.sub(re.escape(q),lambda m:'<mark>'+m[0]+'</mark>',safe,flags=re.I)
  grouped.setdefault(n.image_path,[]).append({'original':s,'highlighted':highlighted,'similarity':float(scores[idx])})
 return [{'image_path':path,'matches':matches} for path,matches in grouped.items()]

# Serve the production frontend and protected API from one HTTPS origin.
from fastapi.staticfiles import StaticFiles
web = FastAPI(title="Study Journal")
web.mount("/api", app)
static_dir = Path(__file__).parent / "static"
if static_dir.is_dir():
    web.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
