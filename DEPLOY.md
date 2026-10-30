# Study Journal - Google Vision 사용 배포본

이 배포본은 기존 화면과 키워드 검색을 유지하고 Google Vision 문서 OCR을 사용합니다. API 키는 파일에 넣지 않습니다.

## GitHub에 올리기
1. GitHub에서 새 저장소를 만듭니다. 저장소 이름 예: study-journal. Private으로 만들어도 Railway에서 연결할 수 있습니다.
2. 압축을 해제하고 폴더 안의 내용을 저장소 루트에 업로드합니다. Dockerfile, railway.toml, frontend, backend가 루트에 보여야 합니다.
3. 로컬에서 사용한 backend/data, node_modules, 인증 파일, API 키는 올리지 않습니다. 이 ZIP에는 포함하지 않았습니다.

## Railway 연결
1. railway.com에서 로그인하고 New Project에서 GitHub 저장소를 선택합니다.
2. 저장소 루트의 Dockerfile로 빌드합니다. Root Directory는 비워둡니다. 별도 Build/Start Command를 입력하지 않습니다.
3. 서비스 Variables에 아래 항목을 설정합니다.
   - OCR_BACKEND: google
   - GOOGLE_VISION_API_KEY: Google Cloud에서 발급받은 실제 API 키
   - STUDY_DATA_DIR: /data
   - SEARCH_BACKEND: keyword
4. 같은 서비스에 Volume을 추가하고 Mount Path를 /data로 설정합니다. 계정과 이미지가 재배포 후에도 유지됩니다. SQLite를 사용하므로 복제본은 1개로 둡니다.
5. Settings > Networking > Generate Domain으로 HTTPS 주소를 만듭니다. 포트 지정이 필요하면 PORT 환경변수에 맞춥니다. 이 앱은 PORT가 없을 때 8000을 사용합니다.
6. 주소의 /api/health/에 접속해 상태를 확인하고, 첫 화면에서 새 계정을 만들어 업로드와 검색을 시험합니다.

## 꼭 알아둘 점
- 로컬 PC에서 만든 계정 및 업로드한 사진은 서버로 자동 이전되지 않습니다.
- 코드만 GitHub에 올리면 호스팅되지 않습니다. Python 서버는 Railway에서 실행합니다.
- 서버 호스팅과 Vision API 사용량에 따라 요금이 발생할 수 있습니다.
- 키는 Railway의 서버 환경변수에만 넣습니다. frontend의 VITE_ 변수에 넣지 않습니다.
- 배포 후에도 기본 검색은 키워드 검색입니다. BGE-M3는 배포본에 설치하지 않았습니다.
- GitHub Pages용 코드가 아닙니다.
