"""Google Vision document/handwriting OCR using a server-side API key.
Set GOOGLE_VISION_API_KEY in the backend process; never use a VITE_ variable.
"""
import base64
import json
import os
import urllib.error
import urllib.request


def extract_text_from_image(image_bytes):
    key = os.getenv('GOOGLE_VISION_API_KEY', '').strip()
    if not key:
        raise RuntimeError('GOOGLE_VISION_API_KEY 환경변수가 없습니다. 서버를 실행한 터미널에서 설정하세요.')
    payload = {'requests': [{
        'image': {'content': base64.b64encode(image_bytes).decode('ascii')},
        'features': [{'type': 'DOCUMENT_TEXT_DETECTION'}],
        'imageContext': {'languageHints': ['ko', 'en']},
    }]}
    request = urllib.request.Request(
        'https://vision.googleapis.com/v1/images:annotate',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'X-Goog-Api-Key': key},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(response.read())
    except urllib.error.HTTPError as error:
        problem = {}
        try:
            problem = json.loads(error.read()).get('error', {})
            status = problem.get('status', '')
        except (ValueError, AttributeError):
            status = ''
        help_text = {
            400: 'API 키 또는 이미지 요청을 확인하세요.',
            401: 'API 인증을 확인하세요.',
            403: 'Vision API 사용 설정, 결제 연결, API 키 제한을 확인하세요.',
            429: '요청 할당량을 초과했습니다. 잠시 후 다시 시도하세요.',
        }.get(error.code, 'Google Vision 요청이 실패했습니다.')
        reasons = [str(detail.get('reason', '')) for detail in problem.get('details', []) if isinstance(detail, dict)]
        message = str(problem.get('message', '')).replace(key, '[REDACTED]')
        reason_text = ','.join(reasons).replace(key, '[REDACTED]')
        raise RuntimeError(f'Google Vision HTTP {error.code} {status}: {help_text} Google reason={reason_text}; message={message}') from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError('Google Vision 연결 실패 또는 시간 초과. 인터넷 연결을 확인하세요.') from None
    responses = result.get('responses', [])
    if not responses:
        raise RuntimeError('Google Vision 응답이 비어 있습니다.')
    item = responses[0]
    if item.get('error'):
        code = item['error'].get('code', 'unknown')
        raise RuntimeError(f'Google Vision 이미지 처리 오류(code={code}). 이미지와 API 설정을 확인하세요.')
    text = item.get('fullTextAnnotation', {}).get('text', '')
    return [line.strip() for line in text.splitlines() if line.strip()]
