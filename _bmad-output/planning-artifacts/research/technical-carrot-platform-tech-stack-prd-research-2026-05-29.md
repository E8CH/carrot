---
stepsCompleted: [1, 2, 6]
inputDocuments: []
workflowType: 'research'
lastStep: 6
research_type: 'technical'
research_topic: '당근마켓 유사 크로스플랫폼 서비스 기술 스택 검증 (PRD 의사결정 근거)'
research_goals: 'PRD 작성을 위한 기술 의사결정 근거 마련. Next.js, Flutter, FastAPI, Supabase/PostgreSQL, Railway 전체 스택 검증. 채팅 구현은 DB 폴링 vs WebSocket/실시간 간단 비교.'
user_name: 'HEMICOLON'
date: '2026-05-29'
web_research_enabled: true
source_verification: true
---

# 기술 리서치 보고서: 당근마켓 유사 크로스플랫폼 서비스

**날짜:** 2026-05-29
**작성자:** HEMICOLON
**리서치 유형:** 기술 스택 검증 (PRD 의사결정 근거)

---

## 핵심 요약 (Executive Summary)

당근마켓 유사 크로스플랫폼 중고거래 서비스의 PRD 작성을 위한 기술 스택 검증 리서치다. 웹 검색 기반으로 2026년 현재 기준 FastAPI·Next.js·Flutter·Supabase·Railway 각 기술의 성숙도와 조합 가능성을 검증했다.

**핵심 결론:**

- 제안된 전체 기술 스택은 2026년 기준 검증된 조합이며 공식 템플릿과 레퍼런스 구현이 존재한다
- Supabase → Railway PostgreSQL 2단계 마이그레이션 경로는 명확하나, Phase 1부터 Supabase 의존 범위(DB+Storage만)를 제한해야 Phase 2 비용이 줄어든다
- 채팅 구현은 DB 폴링(2~3초 간격 REST) 방식이 MVP에 최적 — 구현 단순, 마이그레이션 부담 없음
- `idea.md`의 "Expo Go" 테스트 도구는 Flutter 프로젝트와 충돌하므로 PRD에서 수정 필요

**기술 의사결정 요약:**

| 영역 | 결정 | 근거 |
|------|------|------|
| 인증 | Supabase Auth(JWT 발급) + FastAPI JWT 검증 | Flutter·Next.js 공용, 라이브러리 성숙 |
| 채팅 | DB 폴링 (REST API) | 구현 단순, Phase 2 호환, MVP 허용 지연 |
| 이미지 업로드 | Supabase Storage Presigned URL | 서버 부하 없는 직접 업로드 |
| Phase 2 전환 | DB Dump/Restore 또는 Logical Replication | 공식 Supabase 문서 지원 |
| 모바일 테스트 | Flutter DevTools + 실기기 | Expo Go는 React Native 전용 |

---

## 리서치 범위 확인

**리서치 주제:** 당근마켓 유사 크로스플랫폼 서비스 기술 스택 검증 (PRD 의사결정 근거)

**리서치 목표:** PRD 작성을 위한 기술 의사결정 근거 마련. Next.js, Flutter, FastAPI, Supabase/PostgreSQL, Railway 전체 스택 검증. 채팅 구현은 DB 폴링 vs WebSocket/실시간 간단 비교.

**기술 리서치 범위:**

- 아키텍처 분석 — 설계 패턴, 프레임워크, 시스템 아키텍처
- 구현 접근법 — 개발 방법론, 코딩 패턴
- 기술 스택 — 언어, 프레임워크, 도구, 플랫폼
- 통합 패턴 — API, 프로토콜, 상호 운용성
- 성능 고려사항 — 확장성, 최적화, 패턴

**리서치 방법론:**

- 최신 웹 데이터 기반 소스 검증
- 핵심 기술 주장은 복수 출처 교차 검증
- 불확실한 정보에는 신뢰도 레벨 명시

**범위 확인:** 2026-05-29

---

## UI 레퍼런스 (실제 당근마켓 앱 스크린샷)

리서치 및 PRD 작성 시 아래 실제 앱 화면을 기술 의사결정의 UI 근거로 활용한다.

| 화면 | 주요 UI 요소 | 기술 함의 |
|------|-------------|----------|
| **홈 피드** | 위치 헤더, 카테고리 필터 탭, 썸네일+제목+거리/시간+가격 목록, 상태 배지(예약중), FAB(글쓰기), 하단 탭 5개 | 페이지네이션/무한스크롤, 이미지 최적화, 위치 기반 필터링 API |
| **게시글 작성** | 사진 업로드(최대 10장), 제목/설명 입력, 판매하기/나눔하기 토글, 가격 입력, 거래 희망 장소, 임시저장 | Multipart 업로드, 이미지 스토리지, 폼 상태 관리 |
| **게시글 상세** | 이미지 슬라이더(n/N), 판매자 프로필+매너온도, 상태 표시, 채팅/관심/조회 카운터, 채팅하기+바로구매 버튼 | 이미지 CDN, 매너온도 산출 로직, 채팅방 생성 API |
| **나의 당근** | 관심목록/최근 본 글, 판매관리/구매내역, 설정 아이콘 | 회원별 활동 이력 조회 API, 역할 구분(판매자/구매자 동일 계정) |

---

## 기술 스택 분석

### 1. 프로그래밍 언어 및 프레임워크

#### 백엔드: Python + FastAPI

FastAPI는 2026년 현재 Python 백엔드 프레임워크 중 성장세 1위이며, 자동 OpenAPI 문서 생성, 타입 안전성, 비동기 지원이 핵심 강점이다.

- **비동기 지원:** 데이터베이스 접근, 라우트, 테스트까지 전 레이어 async/await 지원으로 I/O 집약적인 채팅·파일업로드에 적합
- **자동 문서화:** `/docs` (Swagger UI), `/redoc` 자동 생성 → Flutter·Next.js 클라이언트 개발 시 API 계약 즉시 공유 가능
- **SQLModel 통합:** Pydantic + SQLAlchemy 기반 타입 안전 ORM으로 PostgreSQL 스키마와 API 모델 일원화 가능

_신뢰도: 높음_
_출처: [FastAPI Cloud Docs - Supabase Integration](https://fastapicloud.com/docs/integrations/supabase-integration/), [Vinta Software - Next.js FastAPI Template](https://www.vintasoftware.com/blog/next-js-fastapi-template)_

#### 프론트엔드 웹: Next.js (App Router)

- **SSR/SSG:** 게시글 목록·상세 페이지는 SEO가 필요하므로 App Router의 Server Components + SSR 적용 권장
- **TypeScript + Zod:** FastAPI의 Pydantic 스키마와 엔드투엔드 타입 안전성 확보
- **인증:** `next-auth` + FastAPI JWT 검증 패턴이 2026년 표준

_신뢰도: 높음_
_출처: [Vinta Software - Next.js FastAPI Template](https://www.vintasoftware.com/blog/next-js-fastapi-template), [David Crimi - Auth with FastAPI and Next.js](https://www.david-crimi.com/blog/user-auth)_

#### 모바일 앱: Flutter

- **시장 점유율:** 2026년 크로스플랫폼 프레임워크 46% 점유율 1위 유지
- **성능:** Impeller 렌더링 엔진 기반 Android 96%, iOS 91% 네이티브 성능 달성
- **웹 배포:** WebAssembly(Wasm) 기본 빌드로 브라우저 경험도 네이티브에 근접
- **Expo Go 대안:** 기획서의 "Expo Go 테스트"는 React Native 도구이므로 Flutter는 `flutter run` + 실기기/에뮬레이터로 대체

> ⚠️ **의사결정 포인트:** `idea.md`에 "Expo Go"가 테스트 도구로 명시되어 있으나 Flutter 프로젝트와 충돌. Flutter 개발 시 Expo Go는 불필요 — PRD에서 "Flutter DevTools + 실기기 테스트"로 수정 필요.

_신뢰도: 높음_
_출처: [Indujitechnologies - Flutter Cross-Platform 2026](https://www.indujitechnologies.com/blog/flutter-cross-platform-2026), [DEV Community - Flutter vs React Native 2026](https://dev.to/prateekshaweb/flutter-vs-react-native-which-is-better-for-cross-platform-app-development-in-2026-1e5f)_

---

### 2. 데이터베이스 및 스토리지

#### Phase 1: Supabase (BaaS)

Supabase는 PostgreSQL 기반의 BaaS로 인증·스토리지·실시간 기능을 통합 제공한다.

| 기능 | Supabase 제공 | 비고 |
|------|-------------|------|
| 데이터베이스 | PostgreSQL (관리형) | SQLModel/SQLAlchemy로 FastAPI 연결 |
| 인증 | GoTrue (JWT 발급) | FastAPI에서 JWT 검증만 수행 |
| 파일 스토리지 | S3 호환 오브젝트 스토리지 | Presigned URL로 클라이언트 직접 업로드 지원 |
| 실시간 | Realtime (WebSocket) | Phase 1 채팅 구현 옵션 |

**Supabase Storage 이미지 업로드 패턴:**
1. FastAPI 백엔드에서 Presigned Upload URL 생성 (Python SDK)
2. 클라이언트(Flutter/Next.js)가 해당 URL로 직접 업로드 → 서버 부하 없음
3. 업로드 완료 후 Public URL을 DB에 저장

_출처: [Supabase Storage - Presigned URL](https://supabase.com/docs/reference/python/storage-from-createsignedurl), [Supabase Storage v3 Resumable Uploads](https://supabase.com/blog/storage-v3-resumable-uploads)_

#### Phase 2: Railway PostgreSQL (인프라 독립)

- **마이그레이션 방법:** Manual Dump/Restore (모든 Postgres 버전) 또는 Logical Replication (Postgres 10+, 다운타임 최소화)
- **Railway 제공 환경변수:** `DATABASE_URL`, `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` 자동 주입
- **주의사항:** Supabase Auth(GoTrue), Storage, Realtime의 마이그레이션은 DB 마이그레이션과 별도 계획 필요
  - Auth → FastAPI 자체 JWT 발급으로 교체 가능
  - Storage → Railway 볼륨 또는 외부 S3(Cloudflare R2 등)로 대체
  - Realtime → FastAPI WebSocket 또는 폴링으로 대체

> ⚠️ **리스크:** Supabase Storage와 Auth에 깊이 의존할수록 Phase 2 마이그레이션 비용 증가. Phase 1부터 FastAPI를 인증 검증 레이어로 두고 Supabase를 DB+Storage만 활용하는 전략 권장.

_출처: [BuildMVPFast - Supabase vs Railway 2026](https://www.buildmvpfast.com/compare/supabase-vs-railway), [Railway Guides - Self-host Supabase](https://docs.railway.com/guides/supabase)_

---

### 3. 개발 도구 및 플랫폼

#### 버전 관리 및 모노레포

Railway의 공식 템플릿은 Next.js + FastAPI + PostgreSQL 모노레포를 지원한다:
- 서비스별 `root directory` 설정으로 독립 빌드
- `watch paths`로 변경된 서비스만 재배포 트리거
- 권장 구조:

```
/
├── frontend-web/      # Next.js (Railway 서비스 1)
├── backend/           # FastAPI (Railway 서비스 2)
├── mobile/            # Flutter (별도 빌드, Railway 미사용)
└── docs/              # 리서치·기획 문서
```

_출처: [Railway - Deploy Next.js + FastAPI Full-Stack Starter](https://railway.com/deploy/nextjs-fastapi-full-stack-starter), [Railway Guides - Monorepo](https://docs.railway.com/guides/monorepo)_

---

### 4. 통합 패턴: 인증 (JWT 전략)

**통합 JWT 인증 흐름 (Flutter + Next.js 공용):**

```
[Flutter/Next.js]
      │
      ▼
Supabase Auth (회원가입/로그인)
      │ JWT 발급
      ▼
FastAPI (JWT 검증 미들웨어)
      │ 검증 통과 시
      ▼
Supabase DB / 비즈니스 로직
```

- Flutter: JWT를 `flutter_secure_storage`에 저장
- Next.js: JWT를 HTTP-only Cookie에 저장 (`next-auth` + `fastapi-nextauth-jwt` 패키지)
- FastAPI: `python-jose` 또는 `PyJWT`로 Supabase 발급 JWT 검증

**핵심 장점:** 동일한 JWT를 Flutter·Next.js·관리자 웹 모두에서 사용 → 인증 로직 단일화

_신뢰도: 높음_
_출처: [Medium - JWT Authentication with FastAPI and Next.js](https://medium.com/@sl_mar/building-a-secure-jwt-authentication-system-with-fastapi-and-next-js-301e749baec2), [fastapi-nextauth-jwt PyPI](https://pypi.org/project/fastapi-nextauth-jwt/)_

---

### 5. 채팅 구현: DB 폴링 vs Supabase Realtime 비교

프로젝트의 요구사항: **1:1 채팅**, 트래픽은 MVP 수준 (소수 동시 사용자)

#### 옵션 A: DB 폴링 (권장 — MVP)

| 항목 | 내용 |
|------|------|
| **방식** | 클라이언트가 2~3초 간격으로 `GET /chats/{room_id}/messages` 호출 |
| **지연시간** | 2~3초 (MVP 1:1 채팅 허용 범위) |
| **구현 복잡도** | 낮음 — 일반 REST API로 구현, 별도 인프라 없음 |
| **Phase 2 호환** | Railway PostgreSQL 마이그레이션 후 그대로 사용 가능 |
| **단점** | 동시 사용자 증가 시 DB 부하 증가 (MVP에선 문제 없음) |

#### 옵션 B: Supabase Realtime (WebSocket)

| 항목 | 내용 |
|------|------|
| **방식** | Supabase Realtime (Elixir Phoenix 기반 WebSocket) |
| **지연시간** | 쓰기 부하 낮을 때 200ms 이하, 높을 때 500ms~1s |
| **구현 복잡도** | 중간 — Supabase Realtime 구독 설정 필요 |
| **Phase 2 호환** | Supabase 제거 시 WebSocket 서버 별도 구축 필요 → **마이그레이션 비용 발생** |
| **단점** | Phase 2에서 Supabase 의존성 제거 시 재구현 필요 |

> ✅ **의사결정:** MVP는 **DB 폴링(옵션 A)** 채택 권장
> - 구현 시간 절감, Phase 2 마이그레이션 부담 없음
> - 실제 당근마켓 스크린샷 기준 채팅은 실시간성보다 메시지 신뢰성이 우선
> - 향후 트래픽 증가 시 FastAPI WebSocket으로 교체 가능 (API 인터페이스 유지)

_신뢰도: 높음_
_출처: [Supabase Realtime Benchmarks](https://supabase.com/docs/guides/realtime/benchmarks), [Ably - Socket.IO vs Supabase Realtime 2026](https://ably.com/compare/socketio-vs-supabase)_

---

### 6. 클라우드 인프라 및 배포

#### Railway 배포 구성

Railway는 Next.js + FastAPI + PostgreSQL 공식 템플릿을 제공하며, 각 서비스를 독립 컨테이너로 배포한다.

**권장 Railway 서비스 구성:**

| Railway 서비스 | 기술 | 포트 |
|--------------|------|------|
| `backend` | FastAPI (Uvicorn) | 8000 |
| `frontend-web` | Next.js | 3000 |
| `frontend-admin` | Next.js | 3001 |
| `database` | PostgreSQL (Railway 관리형) | 5432 |

- Flutter 앱은 Railway 미사용 → Expo Go 아닌 **Flutter DevTools + 실기기 빌드** (APK/IPA)
- FastAPI는 `Procfile` 또는 `railway.json`으로 Uvicorn 실행 설정
- 환경변수는 Railway 대시보드에서 서비스별 주입

_출처: [Railway - Deploy FastAPI](https://docs.railway.com/guides/fastapi), [Railway - Deploy Next.js with Postgres](https://docs.railway.com/guides/nextjs)_

---

### 7. 기술 채택 트렌드 및 리스크 요약

| 기술 | 성숙도 | 주요 리스크 | 완화 전략 |
|------|--------|------------|----------|
| FastAPI | 높음 | 없음 | — |
| Next.js App Router | 높음 | SSR 캐싱 복잡성 | 정적 페이지는 SSG, 동적은 SSR 명시 |
| Flutter | 높음 | Expo Go 혼동 | PRD에서 Flutter DevTools로 수정 |
| Supabase (Phase 1) | 높음 | Phase 2 마이그레이션 비용 | Auth·Realtime 의존 최소화 |
| Railway | 높음 | 없음 (공식 템플릿 존재) | — |
| DB 폴링 채팅 | 중간 | 동시 사용자 확장 한계 | MVP 이후 WebSocket 전환 계획 수립 |

---

## 참고 출처

- [FastAPI Cloud Docs - Supabase Integration](https://fastapicloud.com/docs/integrations/supabase-integration/)
- [Vinta Software - Next.js FastAPI Template](https://www.vintasoftware.com/blog/next-js-fastapi-template)
- [Indujitechnologies - Flutter Cross-Platform 2026](https://www.indujitechnologies.com/blog/flutter-cross-platform-2026)
- [BuildMVPFast - Supabase vs Railway 2026](https://www.buildmvpfast.com/compare/supabase-vs-railway)
- [Railway Docs - Monorepo Deployment](https://docs.railway.com/guides/monorepo)
- [Railway Docs - Deploy Next.js + FastAPI Full-Stack Starter](https://railway.com/deploy/nextjs-fastapi-full-stack-starter)
- [Railway Docs - Deploy FastAPI](https://docs.railway.com/guides/fastapi)
- [Supabase Realtime Benchmarks](https://supabase.com/docs/guides/realtime/benchmarks)
- [Ably - Socket.IO vs Supabase Realtime 2026](https://ably.com/compare/socketio-vs-supabase)
- [fastapi-nextauth-jwt PyPI](https://pypi.org/project/fastapi-nextauth-jwt/)
- [Supabase Storage - Presigned URL (Python)](https://supabase.com/docs/reference/python/storage-from-createsignedurl)
- [Supabase Storage v3 Resumable Uploads](https://supabase.com/blog/storage-v3-resumable-uploads)
- [Medium - JWT Authentication with FastAPI and Next.js](https://medium.com/@sl_mar/building-a-secure-jwt-authentication-system-with-fastapi-and-next-js-301e749baec2)
- [DEV Community - Flutter vs React Native 2026](https://dev.to/prateekshaweb/flutter-vs-react-native-which-is-better-for-cross-platform-app-development-in-2026-1e5f)

---

**리서치 완료일:** 2026-05-29
**소스 검증:** 웹 검색 기반 다중 출처 교차 검증
**신뢰도:** 높음
