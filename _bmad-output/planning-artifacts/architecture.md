---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-05-29'
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-carrot-2026-05-29/prd.md
  - _bmad-output/planning-artifacts/prds/prd-carrot-2026-05-29/addendum.md
  - _bmad-output/planning-artifacts/research/technical-carrot-platform-tech-stack-prd-research-2026-05-29.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
workflowType: 'architecture'
project_name: 'carrot'
user_name: 'HEMICOLON'
date: '2026-05-29'
---

# Architecture Decision Document — carrot

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**기능 요건 (총 27개: FR-1~FR-26 + FR-14a)**

| 도메인 | FRs | 아키텍처 임팩트 |
|--------|-----|--------------|
| 회원 관리 | FR-1~4 | JWT 인증 미들웨어, role 기반 접근 제어 |
| 게시글 | FR-5~11 | 이미지 업로드(Presigned URL), 무한스크롤 페이지네이션 |
| 채팅 | FR-12~14, FR-14a | DB 폴링 엔드포인트, is_read 상태 추적 |
| 거래 상태 | FR-15~16 | 상태 전이 제어, 구매자 확정 트랜잭션 |
| 후기·매너온도 | FR-17~18 | 매너온도 계산 로직, 1인 1회 제약 |
| 나의 당근 | FR-19~21 | 판매/구매/관심 필터 쿼리 |
| 관리자 | FR-22~26 | 별도 role 검증, 관리자 전용 엔드포인트 |

**비기능 요건 (NFRs)**

| NFR | 아키텍처 영향 |
|-----|------------|
| JWT Bearer 인증 | FastAPI 미들웨어 계층 필수, 3개 클라이언트 공용 |
| Supabase Storage Presigned URL | 이미지 업로드 플로우: 클라이언트 → Supabase 직접, 서버는 URL만 수신 |
| 채팅 폴링 2~3초 | `GET /messages?after={id}` 패턴, 서버 부하 고려한 인덱스 설계 필수 |
| CORS 허용 오리진 명시 | 사용자 웹·관리자 웹·Flutter 3개 오리진 등록 |
| 응답 속도 p95 2초 이내 | 소규모 동시 사용자 기준, 인덱스 최적화로 충분 |
| 이미지 5MB 제한 | 클라이언트 측 사전 검증 + Supabase 정책 이중 적용 |

**DB 마이그레이션 전략**

- Phase 1: Supabase PostgreSQL (BaaS 기반 빠른 개발)
- Phase 2: Railway PostgreSQL (Supabase 의존성 제거 후 자체 관리)
- Supabase Auth/Storage는 교체 가능한 계층으로 추상화 필요

### Scale & Complexity

- **복잡도 수준:** Medium
- **주요 도메인:** Full-stack (3 클라이언트 + API 서버)
- **동시 사용자:** 소규모 (포트폴리오 시연 기준, 성능 목표 완화 적용)
- **예상 아키텍처 컴포넌트:** 12~15개 (라우터 5 + 서비스 5 + DB 모델 5)

| 복잡도 지표 | 여부 |
|-----------|------|
| 실시간 기능 | ❌ 폴링 방식 |
| 멀티테넌시 | ❌ |
| 규제 준수 | ❌ |
| 외부 연동 | ✅ Supabase Auth + Storage |
| 플랫폼 수 | ✅ 4개 |
| 역할 기반 접근 | ✅ user / admin |

### Technical Constraints & Dependencies

| 제약 | 내용 |
|------|------|
| Supabase Auth 의존 | Phase 1 JWT 발급은 Supabase Auth. Phase 2 전환 시 자체 발급으로 교체 |
| Flutter 실기기 배포 | APK/IPA 직접 빌드 (Expo Go 아님) |
| Railway 배포 | Next.js 사용자 웹, Next.js 관리자 웹, FastAPI 각각 독립 서비스 |
| 이미지 업로드 경로 | 클라이언트 → Supabase Storage 직접. FastAPI는 URL만 수신·DB 저장 |
| 채팅 폴링 제약 | SM-C1: 폴링 주기 1초 미만 금지 |

### Cross-Cutting Concerns

1. **인증/인가** — FastAPI JWT 미들웨어 1개로 3개 클라이언트 공용. role 검증(user/admin). 비활성화 회원 JWT 발급 거부 로직 별도 처리.
2. **이미지 생명주기** — Supabase Storage 업로드 → URL 배열 DB 저장 → 게시글 삭제 시 Storage 파일 함께 삭제(A-7).
3. **DB 폴링 인덱스** — `채팅.post_id + sent_at` 복합 인덱스 필수. 폴링 쿼리(`after={last_id}`) 성능 보장.
4. **역할 분리** — 관리자 웹은 별도 URL. 동일 FastAPI에서 role 검증으로 분기.
5. **Cascade 삭제** — 게시글 삭제 → 연결 채팅 메시지 삭제. DB Foreign Key cascade 또는 서비스 레이어 처리 결정 필요.
6. **DB 마이그레이션 추상화** — Supabase → Railway 전환 시 DB 접속 설정만 교체되도록 ORM/쿼리 계층 추상화.

---

## Starter Template Evaluation

### Primary Technology Domain

Full-Stack (4개 플랫폼 병렬 구성) — PRD에서 확정된 스택 반영

### Starter Options Considered

공식 CLI 스타터가 존재하는 플랫폼(Next.js, Flutter)은 공식 도구를 사용하고, FastAPI는 공식 스타터 CLI가 없으므로 2026 best practice 기반 도메인 구조를 수동 구성한다.

---

### 플랫폼 1 & 2: Next.js (사용자 웹 · 관리자 웹)

**선택 스타터:** `create-next-app@latest` (v16.2.6)

**초기화 커맨드:**

```bash
# 사용자 웹
npx create-next-app@latest carrot-web \
  --typescript --eslint --app --src-dir --tailwind

# 관리자 웹
npx create-next-app@latest carrot-admin \
  --typescript --eslint --app --src-dir --tailwind

# shadcn/ui 추가 (각 프로젝트 초기화 직후)
npx shadcn@latest init
```

**스타터가 결정하는 아키텍처 항목:**

| 항목 | 결정값 |
|------|--------|
| 언어 | TypeScript |
| 라우팅 | App Router (`/app` 디렉토리) |
| 스타일링 | Tailwind CSS v4 |
| 컴포넌트 라이브러리 | shadcn/ui (초기화 후 추가) |
| 코드 품질 | ESLint 내장 |
| 폴더 구조 | `src/` 하위 |
| 빌드 도구 | Turbopack (Next.js 16 기본) |

---

### 플랫폼 3: Flutter (모바일)

**선택 스타터:** `flutter create` (Flutter 3.44.0)

**초기화 커맨드:**

```bash
flutter create \
  --org com.carrot \
  --platforms android,ios \
  --template app \
  carrot_mobile
```

**스타터가 결정하는 아키텍처 항목:**

| 항목 | 결정값 |
|------|--------|
| 언어 | Dart |
| UI 프레임워크 | Material 3 (기본 내장) |
| 테마 | ThemeData — light/dark mode 지원 |
| 플랫폼 타겟 | Android + iOS |
| 패키지 관리 | pub.dev |

---

### 플랫폼 4: FastAPI (백엔드)

**선택 스타터:** 수동 구성 — 도메인 기반 구조 (공식 CLI 없음)

**초기 설정:**

```bash
pip install uv
uv venv && uv pip install fastapi uvicorn sqlalchemy[asyncio] alembic
```

**프로젝트 구조:**

```
carrot-api/
├── app/
│   ├── main.py
│   ├── core/              # settings, security, db session
│   ├── api/v1/            # 라우터 조합
│   ├── features/          # 도메인별 모듈
│   │   └── {domain}/
│   │       ├── router.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       ├── schemas.py
│   │       └── models.py
│   └── shared/            # 공통 유틸
├── alembic/
├── tests/
└── pyproject.toml
```

**스타터가 결정하는 아키텍처 항목:**

| 항목 | 결정값 |
|------|--------|
| 언어 | Python 3.12+ |
| ORM | SQLAlchemy 2.0 (Async) |
| 마이그레이션 | Alembic |
| 구조 패턴 | 도메인 기반 (router → service → repository) |
| 패키지 관리 | uv |

> **Note:** 각 플랫폼별 프로젝트 초기화는 구현 첫 스토리(Story 1)에서 진행한다.

---

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (구현 차단 요소):**
- DB Cascade 삭제 방식 → FK Cascade 확정
- 인증 미들웨어 → Supabase Auth JWT (이전 단계 확정)
- 상태 관리 → TanStack Query (Next.js), Riverpod (Flutter) 확정

**Important Decisions (아키텍처 형태 결정):**
- HTTP 클라이언트: Axios (Next.js), http 패키지 (Flutter)
- 캐싱: 미적용 (포트폴리오 규모)

**Deferred Decisions (MVP 이후):**
- Rate Limiting (포트폴리오 시연 범위 외)
- 모니터링/로깅 고도화

---

### Data Architecture

| 결정 | 선택 | 근거 |
|------|------|------|
| Cascade 삭제 | DB FK `ON DELETE CASCADE` | 단순·안전, 누락 불가, 포트폴리오 규모에 적합 |
| 캐싱 전략 | 미적용 | `post_id + sent_at` 복합 인덱스로 폴링 성능 충분, Redis 등 추가 불필요 |
| DB 마이그레이션 | Alembic (SQLAlchemy 2.0) | ORM 계층 추상화로 Supabase → Railway 전환 시 접속 설정만 교체 |

**Cascade 관계:**
```
posts ON DELETE CASCADE → chat_messages
posts ON DELETE CASCADE → likes (관심 목록)
users ON DELETE CASCADE → posts, reviews, chat_messages
```

---

### Authentication & Security

| 결정 | 선택 | 근거 |
|------|------|------|
| 인증 방식 | Supabase Auth JWT 발급 + FastAPI `python-jose` 검증 | 3개 클라이언트 공용 미들웨어 1개 |
| 역할 구분 | JWT payload `role` 필드 (`user` / `admin`) | FastAPI Depends로 라우터별 role 검증 |
| 비활성 계정 | JWT 발급 시 `is_active` 검증 → 발급 거부 | FastAPI 로그인 엔드포인트에서 처리 |
| CORS | FastAPI `CORSMiddleware` — 3개 오리진 명시 허용 | 사용자 웹, 관리자 웹, Flutter(모바일은 CORS 무관) |

---

### API & Communication Patterns

| 결정 | 선택 | 근거 |
|------|------|------|
| API 스타일 | REST (JSON) | PRD 확정 |
| 채팅 폴링 | `GET /api/v1/chats/{room_id}/messages?after={last_message_id}` | 2~3초 간격, 1초 미만 금지(SM-C1) |
| Next.js HTTP 클라이언트 | **Axios** | 인터셉터로 JWT 토큰 자동 주입, 에러 처리 일원화 |
| Flutter HTTP 클라이언트 | **http 패키지** (Flutter 공식) | 의존성 최소화, 포트폴리오 규모에 충분 |
| API 문서화 | FastAPI 내장 **OpenAPI / Swagger UI** 자동 생성 | 별도 작업 불필요 (`/docs`, `/redoc`) |
| 에러 응답 형식 | `{"detail": "메시지", "code": "ERROR_CODE"}` 통일 | FastAPI 커스텀 Exception Handler |

**Axios 인터셉터 패턴 (Next.js):**
```typescript
// 요청 인터셉터: Authorization 헤더 자동 주입
// 응답 인터셉터: 401 → 로그인 페이지 리다이렉트
```

---

### Frontend Architecture

#### Next.js (사용자 웹 · 관리자 웹)

| 결정 | 선택 | 근거 |
|------|------|------|
| 상태 관리 | **TanStack Query** (서버 상태 전담) | 채팅 폴링·게시글 목록 등 서버 상태가 대부분, 별도 글로벌 상태 불필요 |
| 채팅 폴링 구현 | TanStack Query `refetchInterval` | `useQuery({ refetchInterval: 2500 })` |
| 클라이언트 전용 상태 | React `useState` / `useReducer` | 모달·폼 등 로컬 UI 상태만 |

#### Flutter (모바일)

| 결정 | 선택 | 근거 |
|------|------|------|
| 상태 관리 | **Riverpod** | Flutter 현재 표준, 타입 안전, 테스트 용이 |
| 채팅 폴링 | Riverpod `StreamProvider` + Timer | 2~3초 주기 폴링 |
| 테마 | Material 3 + `ThemeData` | light/dark mode 지원 |

---

### Infrastructure & Deployment

| 결정 | 선택 | 근거 |
|------|------|------|
| 배포 플랫폼 | **Railway** | Next.js 사용자 웹, Next.js 관리자 웹, FastAPI 각각 독립 서비스 |
| 환경 변수 | `.env` 파일 (로컬) + **Railway 환경변수** (배포) | 표준 패턴 |
| CI/CD | Railway 자동 배포 (git push → deploy) | 포트폴리오 규모 기준 충분 |
| Flutter 배포 | APK(Android) / IPA(iOS) 직접 빌드 | 실기기 테스트 (Flutter DevTools) |

### Decision Impact Analysis

**구현 우선 순서:**
1. FastAPI core 설정 (JWT 미들웨어, CORS, DB 세션)
2. Alembic 마이그레이션 초기 스키마 (FK CASCADE 포함)
3. Next.js Axios 인스턴스 + TanStack Query 설정
4. Flutter Riverpod 초기화 + http 클라이언트 서비스 클래스

**크로스 컴포넌트 의존성:**
- Axios 인터셉터 ↔ Supabase Auth JWT 토큰 갱신 로직 연동 필요
- Riverpod Provider ↔ Flutter http 패키지 래퍼 서비스 클래스로 추상화
- TanStack Query `refetchInterval` ↔ 채팅 폴링 주기(SM-C1: 1초 미만 금지) 준수

---

## Implementation Patterns & Consistency Rules

### 잠재적 충돌 지점 — 6개 영역 확정

---

### Naming Patterns

#### DB 네이밍 (PostgreSQL)

```
테이블명:     snake_case 복수형      users, posts, chat_messages, likes
컬럼명:       snake_case             user_id, created_at, is_read
FK:           {참조테이블_단수}_id   user_id, post_id
인덱스명:     idx_{테이블}_{컬럼}    idx_chat_messages_post_id_sent_at
```

#### API 엔드포인트 네이밍

```
기본 패턴:    /api/v1/{리소스_복수형}
예시:         /api/v1/users
              /api/v1/posts
              /api/v1/posts/{post_id}/messages
              /api/v1/chats/{room_id}/messages?after={last_message_id}

Path 파라미터:  snake_case   {post_id}, {user_id}, {room_id}
Query 파라미터: snake_case   ?after=123, ?page=1, ?size=20
```

#### 코드 네이밍

**FastAPI (Python)**
```python
# 파일명: snake_case
router.py, service.py, repository.py

# 클래스: PascalCase
class UserService: ...
class PostRepository: ...

# 함수/변수: snake_case
def get_post_by_id(post_id: int): ...
current_user = ...
```

**Next.js (TypeScript)**
```typescript
// 컴포넌트 파일: PascalCase
PostCard.tsx, ChatBubble.tsx, StatusBadge.tsx

// 페이지/레이아웃 파일: Next.js 규칙 (lowercase)
page.tsx, layout.tsx, loading.tsx

// 함수/변수: camelCase
const postId = ...
function getUserPosts() { ... }

// 타입/인터페이스: PascalCase
interface Post { ... }
type UserRole = 'user' | 'admin'
```

**Flutter (Dart)**
```dart
// 파일명: snake_case
post_card.dart, chat_bubble.dart, manner_temp_widget.dart

// 클래스: PascalCase
class PostCard extends StatelessWidget { ... }

// 변수/함수: camelCase
final postId = ...
Future<void> fetchPosts() async { ... }

// Provider: camelCase + Provider 접미사
final postsProvider = ...
final chatMessagesProvider = ...
```

---

### Structure Patterns

#### FastAPI 도메인 구조

```
features/{domain}/
  router.py       # HTTP 엔드포인트만
  service.py      # 비즈니스 로직
  repository.py   # DB 쿼리
  schemas.py      # Pydantic 요청/응답 모델
  models.py       # SQLAlchemy ORM 모델

도메인 목록: users, posts, chats, reviews, admin
```

#### Next.js 라우트 구조

```
src/app/
  (user)/           # 사용자 웹 라우트 그룹
    page.tsx        # 피드 홈
    posts/[id]/
    chat/
    my/
  (admin)/          # 관리자 웹 라우트 그룹
    dashboard/
    users/
    posts/

src/components/
  ui/               # shadcn/ui 기본 컴포넌트
  common/           # 공통 커스텀 컴포넌트 (PostCard, StatusBadge 등)
  {domain}/         # 도메인별 컴포넌트

src/lib/
  api/              # Axios 인스턴스 + API 함수
  hooks/            # 커스텀 훅 (useQuery 래핑 포함)
```

#### Flutter 구조

```
lib/
  features/{domain}/
    data/           # http 클라이언트 호출, DTO
    domain/         # 비즈니스 모델
    presentation/   # Riverpod Provider, Widget
  core/
    api/            # http 클라이언트 설정
    theme/          # ThemeData, 색상 상수
  shared/
    widgets/        # 공통 위젯 (PostCard, ChatBubble 등)
```

---

### Format Patterns

#### API 응답 형식

**단일 객체 (직접 반환):**
```json
{
  "id": 1,
  "title": "아이폰 팝니다",
  "price": 500000,
  "created_at": "2026-05-29T10:00:00Z"
}
```

**목록 응답:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20
}
```

**에러 응답:**
```json
{
  "detail": "게시글을 찾을 수 없습니다.",
  "code": "POST_NOT_FOUND"
}
```

**날짜/시간:** ISO 8601 문자열 (`2026-05-29T10:00:00Z`) — UTC 기준

---

### Communication Patterns

#### TanStack Query queryKey 규칙

```typescript
// 패턴: [리소스, 식별자?, 서브리소스?]
['posts']                          // 게시글 목록
['posts', postId]                  // 게시글 상세
['posts', postId, 'messages']      // 채팅 메시지 목록
['users', userId, 'posts']         // 특정 유저 게시글
['chats']                          // 채팅방 목록

// 채팅 폴링
useQuery({
  queryKey: ['chats', roomId, 'messages'],
  refetchInterval: 2500,  // SM-C1: 1초 미만 금지
})
```

#### Riverpod Provider 규칙

```dart
// 패턴: {리소스}Provider
final postsProvider = ...
final postDetailProvider = ...
final chatMessagesProvider = ...
final userProfileProvider = ...

// 채팅 폴링
final chatMessagesProvider = StreamProvider.autoDispose
  .family<List<Message>, String>((ref, roomId) async* {
    while (true) {
      yield await fetchMessages(roomId, lastId);
      await Future.delayed(Duration(milliseconds: 2500));
    }
  });
```

---

### Process Patterns

#### 에러 처리

**FastAPI:**
```python
# 커스텀 예외 계층
class AppException(Exception):
    def __init__(self, code: str, detail: str, status_code: int): ...

# 전역 핸들러에서 통일 응답 반환
@app.exception_handler(AppException)
async def app_exception_handler(request, exc): ...
```

**Next.js (Axios 인터셉터):**
```typescript
// 401 → 로그인 리다이렉트
// 그 외 → toast 알림 or Error Boundary
```

**Flutter:**
```dart
// try/catch → Riverpod AsyncError 상태로 전파
// UI: AsyncValue.when(data:, loading:, error:) 패턴 통일
```

#### 로딩 상태

| 플랫폼 | 패턴 |
|--------|------|
| Next.js | TanStack Query `isLoading` / `isFetching` → Skeleton UI |
| Flutter | `AsyncValue.loading()` → CircularProgressIndicator |

---

### Enforcement Guidelines

**모든 AI 에이전트가 반드시 따라야 할 규칙:**

1. API JSON 필드는 항상 **snake_case**
2. API 응답은 **래퍼 없이 직접 반환**, 목록은 **items + total**
3. 에러 응답은 반드시 `{"detail": "...", "code": "..."}` 형식
4. 날짜/시간은 **ISO 8601 UTC** 문자열
5. Next.js 컴포넌트 파일은 **PascalCase.tsx**
6. TanStack Query queryKey는 **배열 + 문자열** 패턴
7. Flutter Provider는 **~Provider** 접미사
8. 채팅 폴링 간격은 **2500ms** (SM-C1 준수)
9. FastAPI 라우터는 HTTP 처리만, 로직은 service로 분리

---

## Project Structure & Boundaries

### 저장소 구조: 모노레포

```
carrot/                        # 모노레포 루트
├── carrot-api/                # FastAPI 백엔드
├── carrot-web/                # Next.js 사용자 웹
├── carrot-admin/              # Next.js 관리자 웹
├── carrot-mobile/             # Flutter 모바일
├── .gitignore
└── README.md
```

---

### carrot-api (FastAPI 백엔드)

```
carrot-api/
├── app/
│   ├── main.py                        # FastAPI 앱 생성, 라우터 등록, CORS
│   ├── core/
│   │   ├── config.py                  # Settings (env vars, Supabase URL 등)
│   │   ├── security.py                # JWT 검증 (python-jose)
│   │   ├── database.py                # AsyncSession, engine (SQLAlchemy 2.0)
│   │   └── dependencies.py            # get_current_user, require_admin Depends
│   ├── api/
│   │   └── v1/
│   │       └── router.py              # 모든 도메인 라우터 조합
│   ├── features/
│   │   ├── users/                     # FR-1~4 (회원 관리)
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── posts/                     # FR-5~11, FR-15~16 (게시글·거래 상태)
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── chats/                     # FR-12~14, FR-14a (채팅·폴링)
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── reviews/                   # FR-17~18 (후기·매너온도)
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   └── admin/                     # FR-22~26 (관리자)
│   │       ├── router.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── schemas.py
│   └── shared/
│       ├── exceptions.py              # AppException + 전역 핸들러
│       ├── schemas.py                 # PaginatedResponse (items+total)
│       └── utils.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── unit/features/
│   └── integration/
├── .env
├── .env.example
├── pyproject.toml
├── alembic.ini
├── Dockerfile
└── README.md
```

---

### carrot-web (Next.js 사용자 웹)

```
carrot-web/
├── src/
│   ├── app/
│   │   ├── (user)/
│   │   │   ├── page.tsx               # 피드 홈 (FR-5, FR-6)
│   │   │   ├── posts/
│   │   │   │   ├── [id]/page.tsx      # 게시글 상세 (FR-7)
│   │   │   │   └── new/page.tsx       # 게시글 작성 (FR-8)
│   │   │   ├── chat/
│   │   │   │   ├── page.tsx           # 채팅 목록 (FR-12, FR-14a)
│   │   │   │   └── [roomId]/page.tsx  # 채팅방 (FR-13, FR-14)
│   │   │   └── my/
│   │   │       └── page.tsx           # 나의 당근 (FR-19~21)
│   │   ├── auth/
│   │   │   ├── login/page.tsx         # 로그인 (FR-2)
│   │   │   └── register/page.tsx      # 회원가입 (FR-1)
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   └── not-found.tsx
│   ├── components/
│   │   ├── ui/                        # shadcn/ui 기본 컴포넌트
│   │   ├── common/
│   │   │   ├── PostCard.tsx           # FR-5, FR-6
│   │   │   ├── StatusBadge.tsx        # FR-15, FR-16
│   │   │   ├── MannerTempWidget.tsx   # FR-18
│   │   │   ├── ImageSlider.tsx        # FR-7
│   │   │   └── UnreadBadge.tsx        # FR-14a
│   │   ├── posts/
│   │   │   ├── PostList.tsx
│   │   │   ├── PostForm.tsx
│   │   │   └── TradeCompleteSheet.tsx # FR-16
│   │   ├── chat/
│   │   │   ├── ChatListTile.tsx
│   │   │   └── ChatBubble.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── BottomNav.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── axios.ts               # Axios 인스턴스 + JWT 인터셉터
│   │   │   ├── posts.ts
│   │   │   ├── chats.ts
│   │   │   ├── users.ts
│   │   │   └── reviews.ts
│   │   └── hooks/
│   │       ├── usePosts.ts
│   │       ├── useChats.ts            # refetchInterval: 2500
│   │       └── useAuth.ts
│   ├── types/
│   │   ├── post.ts
│   │   ├── user.ts
│   │   ├── chat.ts
│   │   └── review.ts
│   └── middleware.ts                  # 미인증 → /auth/login 리다이렉트
├── public/
├── .env.local
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── Dockerfile
```

---

### carrot-admin (Next.js 관리자 웹)

```
carrot-admin/
├── src/
│   ├── app/
│   │   ├── (admin)/
│   │   │   ├── dashboard/page.tsx     # 대시보드 (FR-22)
│   │   │   ├── users/
│   │   │   │   ├── page.tsx           # 회원 목록 (FR-23)
│   │   │   │   └── [id]/page.tsx      # 회원 상세/정지 (FR-24)
│   │   │   └── posts/
│   │   │       ├── page.tsx           # 게시글 목록 (FR-25)
│   │   │       └── [id]/page.tsx      # 게시글 삭제 (FR-26)
│   │   ├── auth/
│   │   │   └── login/page.tsx         # 관리자 로그인 (FR-3, FR-4)
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   ├── common/
│   │   │   └── DataTable.tsx
│   │   ├── users/
│   │   │   └── UserTable.tsx
│   │   └── posts/
│   │       └── PostTable.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── axios.ts
│   │   │   ├── admin-users.ts
│   │   │   └── admin-posts.ts
│   │   └── hooks/
│   │       ├── useAdminUsers.ts
│   │       └── useAdminPosts.ts
│   ├── types/
│   └── middleware.ts                  # role=admin 검증
├── .env.local
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── Dockerfile
```

---

### carrot-mobile (Flutter)

```
carrot-mobile/
├── lib/
│   ├── main.dart
│   ├── core/
│   │   ├── api/
│   │   │   ├── api_client.dart        # http 패키지 래퍼 + JWT 헤더
│   │   │   └── api_endpoints.dart     # 엔드포인트 URL 상수
│   │   ├── theme/
│   │   │   ├── app_theme.dart         # ThemeData (Material 3)
│   │   │   └── app_colors.dart
│   │   └── router/
│   │       └── app_router.dart        # go_router
│   ├── features/
│   │   ├── auth/                      # FR-1~2
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   │       ├── login_screen.dart
│   │   │       └── register_screen.dart
│   │   ├── posts/                     # FR-5~11, FR-15~16
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   │       ├── feed_screen.dart
│   │   │       ├── post_detail_screen.dart
│   │   │       └── post_form_screen.dart
│   │   ├── chats/                     # FR-12~14, FR-14a
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   │       ├── chat_list_screen.dart
│   │   │       └── chat_room_screen.dart
│   │   ├── reviews/                   # FR-17~18
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   │       └── review_form_screen.dart
│   │   └── my/                        # FR-19~21
│   │       ├── data/
│   │       ├── domain/
│   │       └── presentation/
│   │           └── my_screen.dart
│   └── shared/
│       └── widgets/                   # UX 명세 커스텀 컴포넌트 8개
│           ├── post_card.dart
│           ├── status_badge.dart
│           ├── manner_temp_widget.dart
│           ├── chat_list_tile.dart
│           ├── chat_bubble.dart
│           ├── image_slider.dart
│           ├── trade_complete_sheet.dart
│           └── unread_badge.dart
├── test/
│   └── features/
├── android/
├── ios/
├── pubspec.yaml
└── README.md
```

---

### Architectural Boundaries

**API 경계:**

| 경계 | 규칙 |
|------|------|
| 공개 엔드포인트 | `POST /api/v1/auth/login`, `POST /api/v1/auth/register` |
| 인증 필요 | 나머지 모든 엔드포인트 — JWT Bearer 필수 |
| 관리자 전용 | `/api/v1/admin/**` — role=admin 추가 검증 |
| 이미지 업로드 | 클라이언트 → Supabase Storage 직접 (FastAPI 미경유) |

**데이터 흐름:**

```
[Next.js / Flutter]
    ↓ Axios / http (JWT Bearer)
[FastAPI /api/v1/]
    ↓ SQLAlchemy AsyncSession
[PostgreSQL (Supabase Phase1 → Railway Phase2)]

[이미지 업로드]
클라이언트 → Supabase Storage (Presigned URL 직접 업로드)
    → URL만 FastAPI로 전달 → DB 저장
```

**컴포넌트 경계:**

```
carrot-web / carrot-admin
  lib/api/*.ts           ← FastAPI 호출 전담
  lib/hooks/*.ts         ← TanStack Query 래핑, UI와 분리

carrot-mobile
  core/api/api_client.dart   ← http 호출 전담
  features/*/data/           ← Provider에서 호출
  features/*/presentation/   ← UI, Provider 구독만
```

### Requirements → Structure 매핑

| FR 범위 | 위치 |
|---------|------|
| FR-1~4 (회원·관리자 인증) | `carrot-api/features/users/`, `carrot-api/features/admin/`, `auth/` 페이지 |
| FR-5~11 (게시글) | `carrot-api/features/posts/`, `carrot-web/(user)/posts/`, `carrot-mobile/features/posts/` |
| FR-12~14a (채팅·폴링) | `carrot-api/features/chats/`, `carrot-web/(user)/chat/`, `carrot-mobile/features/chats/` |
| FR-15~16 (거래 상태) | `carrot-api/features/posts/` (상태 전이), `TradeCompleteSheet` 컴포넌트 |
| FR-17~18 (후기·매너온도) | `carrot-api/features/reviews/`, `carrot-mobile/features/reviews/` |
| FR-19~21 (나의 당근) | `carrot-web/(user)/my/`, `carrot-mobile/features/my/` |
| FR-22~26 (관리자) | `carrot-api/features/admin/`, `carrot-admin/(admin)/` |

---

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:** TypeScript(Next.js) · Python(FastAPI) · Dart(Flutter) 3개 스택이 REST API로만 통신하므로 언어 간 충돌 없음. SQLAlchemy 2.0 Async는 FastAPI의 async 라우터와 완전 호환.

**Pattern Consistency:** snake_case JSON, 직접 반환, items+total 페이지네이션이 FastAPI 기본 동작과 일치하여 별도 변환 레이어 불필요.

**Structure Alignment:** 도메인 기반 구조(features/)가 5개 도메인(users, posts, chats, reviews, admin) 각각에 완전 매핑됨.

---

### 보완: 이미지 업로드 & 삭제 흐름

**Presigned URL 발급 흐름:**
```
1. 클라이언트 → FastAPI: POST /api/v1/posts/upload-url
2. FastAPI → Supabase Storage SDK: presigned URL 발급
3. FastAPI → 클라이언트: presigned URL 반환
4. 클라이언트 → Supabase Storage: 직접 PUT 업로드
5. 클라이언트 → FastAPI: 업로드된 파일 URL 포함하여 게시글 생성/수정
```

**이미지 삭제 순서 (게시글 삭제 시, A-7):**
```python
# posts/service.py 내 delete_post()
async def delete_post(post_id: int):
    post = await repository.get_post(post_id)
    # 1. Supabase Storage 파일 삭제 (먼저)
    for image_url in post.image_urls:
        await supabase_storage.delete(image_url)
    # 2. DB 레코드 삭제 (FK CASCADE가 chat_messages, likes 자동 삭제)
    await repository.delete_post(post_id)
```

**이미지 5MB 클라이언트 검증 위치:**
- `carrot-web`: `src/components/posts/PostForm.tsx` — input onChange 핸들러
- `carrot-mobile`: `lib/features/posts/presentation/post_form_screen.dart` — 파일 선택 후 즉시 검증

---

### Requirements Coverage Validation ✅

| FR 범위 | 커버 여부 |
|---------|----------|
| FR-1~4 회원·인증 | ✅ |
| FR-5~11 게시글 | ✅ |
| FR-12~14a 채팅·폴링·미읽음 | ✅ |
| FR-15~16 거래 상태 | ✅ |
| FR-17~18 후기·매너온도 | ✅ |
| FR-19~21 나의 당근 | ✅ |
| FR-22~26 관리자 | ✅ |
| NFR JWT 인증 | ✅ |
| NFR Presigned URL 업로드 | ✅ |
| NFR 채팅 폴링 2~3초 | ✅ |
| NFR CORS | ✅ |
| NFR 이미지 5MB 제한 | ✅ |

### Architecture Completeness Checklist

**Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

---

### Architecture Readiness Assessment

**Overall Status: READY FOR IMPLEMENTATION** ✅

**Confidence Level:** High

**Key Strengths:**
- 4개 플랫폼이 REST API로만 통신 → 언어 간 결합 없음
- 도메인 기반 구조로 AI 에이전트 간 작업 영역 명확히 분리
- 9개 강제 규칙으로 에이전트 충돌 지점 사전 차단
- 채팅 폴링 제약(SM-C1)이 구현 패턴 레벨까지 명시됨

**Areas for Future Enhancement:**
- Phase 2: Supabase → Railway DB 마이그레이션 시 auth 자체 발급으로 교체
- Rate Limiting (포트폴리오 이후 실서비스 전환 시)
- 모니터링/로깅 고도화

### Implementation Handoff

**AI 에이전트 지침:**
1. 이 문서의 모든 결정을 그대로 따를 것
2. 구현 패턴 섹션의 9개 강제 규칙을 항상 준수할 것
3. 프로젝트 구조를 벗어난 파일 생성 금지
4. 아키텍처 질문은 이 문서를 최우선 참조할 것

**첫 구현 단계:**
```bash
# 1. 모노레포 루트 생성
mkdir carrot && cd carrot

# 2. FastAPI 초기화
mkdir carrot-api && cd carrot-api
uv venv && uv pip install fastapi uvicorn sqlalchemy[asyncio] alembic python-jose

# 3. Next.js 사용자 웹 초기화
npx create-next-app@latest carrot-web --typescript --eslint --app --src-dir --tailwind

# 4. Next.js 관리자 웹 초기화
npx create-next-app@latest carrot-admin --typescript --eslint --app --src-dir --tailwind

# 5. Flutter 초기화
flutter create --org com.carrot --platforms android,ios --template app carrot-mobile
```
