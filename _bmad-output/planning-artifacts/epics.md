---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
completedAt: '2026-05-29'
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-carrot-2026-05-29/prd.md
  - _bmad-output/planning-artifacts/prds/prd-carrot-2026-05-29/addendum.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - _bmad-output/planning-artifacts/architecture.md
---

# carrot - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for carrot, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: 회원은 이메일·비밀번호·주소·연락처를 입력하여 계정을 생성할 수 있다. (중복 이메일 에러, 비밀번호 8자 이상, 가입 성공 시 JWT 발급 후 홈 피드 이동)
FR-2: 회원은 이메일·비밀번호로 인증하여 JWT를 발급받을 수 있다. (잘못된 자격증명 시 에러, JWT는 이후 모든 인증 요청 헤더에 포함)
FR-3: 로그인한 회원은 클라이언트에서 JWT를 제거하여 로그아웃할 수 있다. (로그아웃 후 인증 필요 화면 접근 시 로그인 화면으로 리다이렉트)
FR-4: 로그인한 회원은 자신의 프로필(이메일·주소·연락처·매너온도)을 조회할 수 있다. (매너온도 소수점 1자리 표시)
FR-5: 로그인한 회원은 사진·제목·설명·가격(또는 나눔)·거래 희망 장소를 입력하여 게시글을 등록할 수 있다. (사진 1장 이상 최대 10장, 제목·설명 필수, 등록 후 상태 '판매중')
FR-6: 게시글 작성 중 회원은 임시저장할 수 있으며, 다음 작성 시 이어서 편집할 수 있다. (계정당 임시저장 1개, 임시저장 게시글은 목록 미노출)
FR-7: 비로그인 포함 모든 사용자는 게시글 목록을 최신순으로 조회할 수 있다. (대표 사진·제목·가격·상태 배지·채팅 수·관심 수 표시, 20개씩 무한 스크롤, 거래완료 게시글도 노출)
FR-8: 사용자는 게시글을 클릭하여 전체 정보(이미지 슬라이더·판매자 프로필·매너온도·제목·가격·설명·상태·채팅 수·관심 수·조회 수)를 조회할 수 있다. (조회 수 매 조회마다 +1, 판매자 본인은 수정/삭제 버튼 노출)
FR-9: 판매자는 자신의 게시글(제목·설명·사진·가격·거래 희망 장소)을 수정할 수 있다. (본인 게시글만, 수정 후 updated 타임스탬프 갱신)
FR-10: 판매자는 자신의 게시글을 삭제할 수 있다. (본인 게시글만, 삭제 시 Supabase Storage 이미지 먼저 삭제 후 DB 레코드 삭제, 연결 채팅 메시지 FK CASCADE 삭제)
FR-11: 로그인한 회원은 게시글을 찜(관심 등록/해제)할 수 있다. (찜 수 목록·상세 반영, 찜한 게시글은 나의 당근 > 관심목록에서 확인)
FR-12: 로그인한 회원은 자신이 판매자가 아닌 게시글에서 "채팅하기"를 눌러 채팅방을 생성할 수 있다. (동일 게시글+구매자 조합 중복 시 기존 방으로 이동, 판매자 본인 게시글은 채팅하기 비활성)
FR-13: 채팅방 참여자(판매자·구매자)는 텍스트 메시지를 전송하고 수신할 수 있다. (메시지 DB 저장, 2~3초 폴링 수신, 전송 실패 시 에러 표시)
FR-14: 로그인한 회원은 자신이 참여 중인 채팅방 목록을 조회할 수 있다. (게시글 썸네일·상대방 이름·마지막 메시지 미리보기·경과 시간 표시, 최근 메시지 기준 내림차순)
FR-14a: 새 메시지가 수신되었으나 읽지 않은 채팅방이 있을 경우 하단 탭 채팅 메뉴에 미읽음 채팅방 수 배지(+N) 표시. (미읽음 채팅방 수 기준, 입장 시 해소, 2~3초 폴링 주기)
FR-15: 판매자는 게시글 상세 또는 채팅방에서 거래 상태를 '판매중'/'예약중'/'거래완료' 중 하나로 변경할 수 있다. (판매자 본인만, 변경 즉시 목록·상세 배지 반영, 거래완료 시 구매자 지정 필수)
FR-16: 판매자가 '거래완료'로 상태 변경 시 해당 게시글의 구매자를 확정한다. (buyer_email 저장, 확정 후 양측에 후기 작성 알림 노출)
FR-17: 거래완료 확정 후 판매자와 구매자 각각 상대방에게 후기를 1회 작성할 수 있다. (동일 거래 1인 1회, 작성 후 상대방 매너온도 즉시 반영)
FR-18: 모든 회원의 프로필과 게시글 상세에 매너온도가 표시된다. (신규 회원 36.5℃ 시작, 긍정 +1℃ / 부정 -1℃, 최솟값 0℃ 최댓값 99℃)
FR-19: 회원은 자신이 등록한 게시글 목록을 상태별(판매중·예약중·거래완료)로 조회할 수 있다. (각 게시글에서 상태 변경 버튼 접근 가능)
FR-20: 회원은 자신이 구매자로 확정된 거래완료 게시글 목록을 조회할 수 있다. (게시글 제목·대표 사진·가격·거래완료 날짜 표시)
FR-21: 회원은 찜한 게시글 목록을 조회할 수 있다. (삭제된 게시글은 자동 제거)
FR-22: 관리자 전용 웹에서 이메일·비밀번호로 관리자 계정을 생성할 수 있다. (role=admin 저장, 관리자 전용 웹 URL로만 접근 가능)
FR-23: 관리자는 이메일·비밀번호로 로그인하여 대시보드에 접근할 수 있다. (role=admin 아닌 계정 접근 거부, 성공 시 대시보드로 이동)
FR-24: 관리자는 전체 회원 목록을 조회하고 특정 회원의 계정을 활성화/비활성화할 수 있다. (비활성화 시 JWT 발급 거부, 목록에 이메일·가입일·매너온도·게시글 수 표시)
FR-25: 관리자는 전체 게시글 목록을 조회하고 상태를 확인할 수 있다. (상태별 필터 제공, 게시글 강제 삭제 가능)
FR-26: 관리자는 전체 채팅 내역을 조회할 수 있다. (채팅방 목록에 판매자·구매자·게시글·메시지 수 표시, 특정 채팅방 메시지 내역 열람)

### NonFunctional Requirements

NFR-1: 모든 인증 필요 API는 JWT Bearer 토큰 검증 (FastAPI 미들웨어). 토큰 만료 시 401 반환.
NFR-2: 이미지 업로드는 Supabase Storage Presigned URL 방식. 클라이언트가 직접 업로드, 서버는 URL만 수신·저장. 이미지당 최대 5MB.
NFR-3: 채팅 클라이언트는 2~3초 간격으로 신규 메시지를 조회. 폴링 간격 1초 미만 금지(SM-C1).
NFR-4: 사용자 웹·관리자 웹·Flutter 앱 도메인에 대해 CORS 허용 오리진 명시.
NFR-5: 게시글 목록 API p95 응답 2초 이내 (MVP 기준 소규모 동시 사용자).

### Additional Requirements

- AR-1: 모노레포 루트 생성 (carrot-api / carrot-web / carrot-admin / carrot-mobile 4개 하위 프로젝트)
- AR-2: 각 플랫폼 스타터 초기화 — create-next-app (carrot-web, carrot-admin), flutter create (carrot-mobile), FastAPI 수동 구성 (carrot-api)
- AR-3: Alembic 초기 마이그레이션 — DB 스키마 생성 (users, posts, chats, reviews, likes 테이블 + FK CASCADE + 복합 인덱스 `idx_chat_messages_post_id_sent_at`)
- AR-4: FastAPI core 설정 — JWT 미들웨어, CORS, AsyncSession DB 세션, AppException 전역 핸들러
- AR-5: Presigned URL 발급 엔드포인트 구현 (`POST /api/v1/posts/upload-url`)
- AR-6: 게시글 삭제 시 Supabase Storage 이미지 파일 먼저 삭제 후 DB 레코드 삭제 (service.py 명시적 처리)
- AR-7: Railway 배포 설정 — carrot-api, carrot-web, carrot-admin 각각 독립 서비스
- AR-8: Axios 인스턴스 설정 (JWT 인터셉터, 401 리다이렉트) — carrot-web, carrot-admin 각각
- AR-9: TanStack Query 설정 (QueryClient, queryKey 컨벤션) — carrot-web, carrot-admin
- AR-10: Riverpod 초기화 + http 패키지 API 클라이언트 서비스 클래스 — carrot-mobile

### UX Design Requirements

UX-DR1: 색상 시스템 구현 — Primary #FF7E36, primary-hover #E86D28, 중립 gray 스케일, 시맨틱 컬러(success/warning/error/info), 매너온도 전용 컬러(0~30℃ 파랑, 36.5~50℃ 오렌지, 50~99℃ 빨강) — Next.js tailwind.config + Flutter ThemeData
UX-DR2: 타이포그래피 시스템 구현 — text-2xl(24px/700)~text-xs(12px/400) 6단계 스케일, 시스템 폰트 스택
UX-DR3: PostCard 공통 컴포넌트 — 좌 썸네일(100×100px) + 우 텍스트(제목·가격·상태 배지·채팅수·관심수·경과시간), 전 플랫폼 공통 시각 언어
UX-DR4: StatusBadge 공통 컴포넌트 — 판매중(없음)/예약중(회색 #6B7280)/거래완료(진한 #374151), 게시글 썸네일 좌상단 오버레이
UX-DR5: MannerTempWidget 컴포넌트 — 🥕 아이콘 + 숫자 + 색상 그라데이션, 온도 범위별 색상 변화
UX-DR6: ChatListTile 컴포넌트 — 게시글 썸네일 + 상대방 이름 + 마지막 메시지 미리보기 + 경과 시간 + 미읽음 배지
UX-DR7: ChatBubble 컴포넌트 — 내 메시지(오렌지 우측) / 상대 메시지(회색 좌측), 낙관적 UI '전송 중' 아이콘
UX-DR8: ImageSlider 컴포넌트 — 게시글 상세 상단 전체 너비, 가로 스와이프, 인디케이터 점 표시
UX-DR9: TradeCompleteSheet 컴포넌트 — 거래완료 바텀시트: 구매자 지정 → 체크 애니메이션(1초) → 후기 작성 CTA 자동 연결 단일 플로우
UX-DR10: UnreadBadge 컴포넌트 — 채팅 탭 +N 미읽음 배지
UX-DR11: 낙관적 UI 메시지 전송 — 전송 즉시 말풍선 노출 + '전송 중' 아이콘 → 폴링 확인 후 제거
UX-DR12: 무한 스크롤 — 홈 피드 20개씩 추가 로딩, 하단 스피너
UX-DR13: Flutter 하단 3탭 NavigationBar — 홈/채팅(미읽음 배지)/나의당근
UX-DR14: Flutter FAB — 우하단 오렌지 원형 FloatingActionButton (글쓰기 진입)
UX-DR15: 관리자 웹 사이드바 네비게이션 + DataTable — shadcn DataTable, 오렌지 액센트 유지
UX-DR16: 접근성 — 터치 타겟 최소 44×44px, WCAG AA 색상 대비, 키보드 포커스 표시

### FR Coverage Map

FR-1: Epic 1 — 회원가입
FR-2: Epic 1 — 로그인
FR-3: Epic 1 — 로그아웃
FR-4: Epic 1 — 프로필 조회
FR-5: Epic 2 — 게시글 작성
FR-6: Epic 2 — 임시저장
FR-7: Epic 2 — 홈 피드 (게시글 목록)
FR-8: Epic 2 — 게시글 상세 조회
FR-9: Epic 2 — 게시글 수정
FR-10: Epic 2 — 게시글 삭제
FR-11: Epic 2 — 게시글 찜 (관심)
FR-12: Epic 3 — 채팅방 생성
FR-13: Epic 3 — 메시지 전송·수신
FR-14: Epic 3 — 채팅 목록 조회
FR-14a: Epic 3 — 미읽음 배지
FR-15: Epic 4 — 거래 상태 변경
FR-16: Epic 4 — 구매자 확정
FR-17: Epic 4 — 후기 작성
FR-18: Epic 4 — 매너온도 표시
FR-19: Epic 5 — 판매관리
FR-20: Epic 5 — 구매내역
FR-21: Epic 5 — 관심목록
FR-22: Epic 6 — 관리자 회원가입
FR-23: Epic 6 — 관리자 로그인
FR-24: Epic 6 — 회원 관리
FR-25: Epic 6 — 거래 관리
FR-26: Epic 6 — 채팅 관리

## Epic List

### Epic 1: 플랫폼 초기화 & 회원 인증
회원이 가입·로그인·로그아웃하고 프로필을 조회할 수 있는 완전한 인증 시스템. 모노레포 환경과 4개 플랫폼 기반 구성을 포함하며, 이후 모든 Epic의 토대가 된다.
**FRs covered:** FR-1, FR-2, FR-3, FR-4
**AR covered:** AR-1, AR-2, AR-3, AR-4, AR-8, AR-9, AR-10
**UX covered:** UX-DR1, UX-DR2, UX-DR13, UX-DR14, UX-DR16

### Epic 2: 게시글 등록 & 피드 탐색
판매자는 사진과 함께 물품을 등록·수정·삭제하고, 구매자는 홈 피드에서 게시글을 탐색·조회·찜할 수 있다.
**FRs covered:** FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11
**AR covered:** AR-5, AR-6
**UX covered:** UX-DR3, UX-DR4, UX-DR5, UX-DR8, UX-DR12

### Epic 3: 1:1 채팅
구매자와 판매자가 게시글 기반 1:1 채팅방을 생성하고 실시간처럼 메시지를 주고받을 수 있다. 미읽음 배지와 낙관적 UI 포함.
**FRs covered:** FR-12, FR-13, FR-14, FR-14a
**UX covered:** UX-DR6, UX-DR7, UX-DR10, UX-DR11

### Epic 4: 거래 완료 & 후기·매너온도
판매자가 거래 상태를 변경하고 구매자를 확정하며, 양측이 후기를 작성해 매너온도를 쌓는 거래 신뢰 시스템 완성.
**FRs covered:** FR-15, FR-16, FR-17, FR-18
**UX covered:** UX-DR9

### Epic 5: 나의 당근 (마이페이지)
회원이 자신의 판매관리·구매내역·관심목록을 한 곳에서 확인하고 관리할 수 있다.
**FRs covered:** FR-19, FR-20, FR-21

### Epic 6: 관리자 웹
관리자가 전용 웹에서 가입·로그인하고, 회원 계정 관리·게시글 관리·채팅 내역 열람을 수행할 수 있다.
**FRs covered:** FR-22, FR-23, FR-24, FR-25, FR-26
**AR covered:** AR-7
**UX covered:** UX-DR15

---

## Epic 1: 플랫폼 초기화 & 회원 인증

회원이 가입·로그인·로그아웃하고 프로필을 조회할 수 있는 완전한 인증 시스템. 모노레포 환경과 4개 플랫폼 기반 구성을 포함하며, 이후 모든 Epic의 토대가 된다.

### Story 1.1: 프로젝트 기반 환경 설정

As a developer,
I want the monorepo and all 4 platform projects initialized with core infrastructure,
So that feature development can begin immediately with a consistent foundation.

**Acceptance Criteria:**

**Given** 빈 디렉토리에서 시작할 때
**When** 초기화 커맨드를 실행하면
**Then** `carrot/` 모노레포 루트 하위에 `carrot-api/`, `carrot-web/`, `carrot-admin/`, `carrot-mobile/` 4개 프로젝트가 생성된다
**And** `carrot-api/`는 FastAPI + SQLAlchemy 2.0 Async + Alembic이 설치되고 `GET /health` 엔드포인트가 200을 반환한다
**And** `carrot-web/`과 `carrot-admin/`은 Next.js 16 + TypeScript + Tailwind CSS + shadcn/ui가 초기화된다
**And** `carrot-mobile/`은 Flutter 3탭 NavigationBar(홈/채팅/나의당근)가 구성된다
**And** `carrot-web/`과 `carrot-admin/`의 `tailwind.config`에 carrot 색상 토큰(Primary #FF7E36 등)이 등록된다
**And** `carrot-mobile/`의 `ThemeData`에 `ColorScheme.fromSeed(Color(0xFFFF7E36))`가 적용된다
**And** `carrot-web/`과 `carrot-admin/`에 Axios 인스턴스(`src/lib/api/axios.ts`)와 TanStack Query `QueryClient`가 설정된다
**And** `carrot-mobile/`에 Riverpod `ProviderScope`와 `ApiClient` 서비스 클래스가 설정된다
**And** 각 플랫폼에 `.env.example` 파일이 생성된다

### Story 1.2: 회원가입

As a 신규 사용자,
I want to create an account with email, password, address, and phone number,
So that I can access all features of the carrot service.

**Acceptance Criteria:**

**Given** Alembic `users` 테이블 마이그레이션이 완료된 상태에서
**When** 유효한 이메일·비밀번호(8자 이상)·주소·연락처로 `POST /api/v1/auth/register`를 호출하면
**Then** 비밀번호가 bcrypt로 해시되어 DB에 저장되고 JWT가 반환된다
**And** `role: user`, `is_active: true`, `manner_temp: 36.5`로 초기화된다

**Given** 이미 가입된 이메일로 가입을 시도하면
**When** `POST /api/v1/auth/register`를 호출하면
**Then** `{"detail": "이미 사용 중인 이메일입니다.", "code": "EMAIL_ALREADY_EXISTS"}` 에러가 반환된다

**Given** Next.js 회원가입 페이지(`/auth/register`)에서
**When** 폼을 작성하고 제출하면
**Then** 성공 시 JWT가 저장되고 홈 피드(`/`)로 이동한다
**And** 실패 시 인라인 에러 메시지가 표시된다

**Given** Flutter 회원가입 화면에서
**When** 폼을 작성하고 제출하면
**Then** 성공 시 JWT가 저장되고 홈 피드(NavigationBar 홈 탭)로 이동한다

### Story 1.3: 로그인 & 로그아웃

As a 가입된 회원,
I want to log in with my email and password and log out when done,
So that I can securely access my account and protect it when I'm finished.

**Acceptance Criteria:**

**Given** 활성 계정의 올바른 자격증명으로
**When** `POST /api/v1/auth/login`을 호출하면
**Then** JWT가 반환된다

**Given** 잘못된 자격증명으로 로그인을 시도하면
**When** `POST /api/v1/auth/login`을 호출하면
**Then** `{"detail": "이메일 또는 비밀번호가 올바르지 않습니다.", "code": "INVALID_CREDENTIALS"}` 에러가 반환된다

**Given** 비활성화된 계정으로 로그인을 시도하면
**When** `POST /api/v1/auth/login`을 호출하면
**Then** `{"detail": "비활성화된 계정입니다.", "code": "ACCOUNT_INACTIVE"}` 에러가 반환된다

**Given** Next.js에서 로그인 성공 후
**When** 인증이 필요한 페이지에 접근하면
**Then** 정상 접근이 가능하고, 로그아웃 후 접근 시 `/auth/login`으로 리다이렉트된다

**Given** Flutter에서 로그인 성공 후
**When** 로그아웃을 탭하면
**Then** JWT가 삭제되고 로그인 화면으로 이동한다

**Given** Axios 인터셉터가 설정된 상태에서
**When** 만료된 JWT로 API를 호출하면
**Then** 401 응답을 받고 자동으로 로그인 페이지로 리다이렉트된다

### Story 1.4: 회원 프로필 조회

As a 로그인한 회원,
I want to view my profile including email, address, phone number, and manner temperature,
So that I can confirm my account information and current trust score.

**Acceptance Criteria:**

**Given** 로그인한 회원이
**When** `GET /api/v1/users/me`를 호출하면
**Then** `{email, address, phone, role, manner_temp, created_at}` 형식의 데이터가 반환된다
**And** `manner_temp`는 소수점 1자리로 반환된다

**Given** JWT 없이 `GET /api/v1/users/me`를 호출하면
**When** 요청이 전송되면
**Then** 401이 반환된다

**Given** Next.js 나의 당근 탭(`/my`)에서
**When** 페이지가 로드되면
**Then** 회원의 이메일·주소·연락처·매너온도가 표시된다
**And** 매너온도는 MannerTempWidget으로 렌더링된다

**Given** Flutter 나의당근 탭에서
**When** 탭에 진입하면
**Then** 동일한 프로필 정보와 MannerTempWidget이 표시된다

---

## Epic 2: 게시글 등록 & 피드 탐색

판매자는 사진과 함께 물품을 등록·수정·삭제하고, 구매자는 홈 피드에서 게시글을 탐색·조회·찜할 수 있다.

### Story 2.1: 홈 피드 (게시글 목록 조회)

As a 사용자 (비로그인 포함),
I want to browse a list of posts sorted by newest first,
So that I can discover items available for sale.

**Acceptance Criteria:**

**Given** 누구든 (비로그인 포함)
**When** `GET /api/v1/posts?page=1&size=20`을 호출하면
**Then** `{items: [...], total: N, page: 1, size: 20}` 형식으로 최신순 게시글 목록이 반환된다
**And** 각 항목에 `id, title, price, is_free, status, photos[0], chat_count, like_count, created_at`이 포함된다
**And** 거래완료 게시글도 목록에 포함된다
**And** `posts`, `likes` 테이블은 Story 1.1 초기 마이그레이션(AR-3)에서 이미 생성됨

**Given** Next.js 홈 피드(`/`)에서
**When** 페이지가 로드되면
**Then** PostCard 목록이 렌더링된다 (좌 썸네일 100×100px + 우 제목·가격·StatusBadge·채팅수·관심수·경과시간)
**And** 스크롤이 하단에 도달하면 다음 20개를 자동 로드한다 (무한 스크롤)

**Given** Flutter 홈 탭에서
**When** 피드가 로드되면
**Then** PostCard 위젯 ListView가 렌더링되고 무한 스크롤이 동작한다

### Story 2.2: 게시글 작성 & 이미지 업로드

As a 로그인한 판매자,
I want to create a post with photos, title, description, price, and trade location,
So that buyers can find and contact me about my item.

**Acceptance Criteria:**

**Given** 로그인한 회원이
**When** `POST /api/v1/posts/upload-url`을 호출하면
**Then** Supabase Storage Presigned URL이 반환된다

**Given** Presigned URL로 이미지를 업로드한 후
**When** `POST /api/v1/posts`를 호출하면
**Then** 게시글이 `status: 판매중`으로 생성되고 생성된 게시글 데이터가 반환된다
**And** 사진이 1장 미만이면 `{"detail": "사진을 1장 이상 업로드해야 합니다.", "code": "PHOTO_REQUIRED"}` 에러가 반환된다

**Given** Next.js 게시글 작성 페이지(`/posts/new`)에서 사진 선택 시
**When** 5MB 초과 이미지를 선택하면
**Then** 즉시 에러 토스트가 표시되어 선택이 거부된다
**And** 정상 작성 완료 후 "등록됐어요!" 토스트와 함께 홈 피드로 이동한다

**Given** Flutter 게시글 작성 화면에서
**When** 우하단 FAB을 탭하면
**Then** 갤러리 권한 요청이 표시되고 허용 후 사진 선택 화면으로 이동한다
**And** 동일한 폼 유효성 검사와 Presigned URL 업로드 흐름이 적용된다

### Story 2.3: 임시저장

As a 로그인한 판매자,
I want to save my post draft and resume editing later,
So that I don't lose my work if I need to stop mid-way.

**Acceptance Criteria:**

**Given** 로그인한 회원이 게시글 작성 중 "임시저장" 버튼을 탭하면
**When** `POST /api/v1/posts/draft`를 호출하면
**Then** 현재 입력 내용이 저장된다 (계정당 1개, 기존 임시저장이 있으면 덮어씀)
**And** 임시저장된 게시글은 `GET /api/v1/posts` 목록에 포함되지 않는다

**Given** 임시저장이 있는 회원이 게시글 작성 화면을 열면
**When** 작성 화면이 로드되면
**Then** "이전에 작성 중인 글이 있어요. 이어서 작성하시겠어요?" 안내가 표시되고 확인 시 내용이 복원된다

### Story 2.4: 게시글 상세 조회

As a 사용자,
I want to view the full details of a post including all photos, seller info, and manner temperature,
So that I can decide whether to contact the seller.

**Acceptance Criteria:**

**Given** 누구든
**When** `GET /api/v1/posts/{post_id}`를 호출하면
**Then** `{photos[], title, description, price, is_free, status, trade_place, view_count, chat_count, like_count, seller_email, manner_temp}`가 반환된다
**And** 조회 시마다 `view_count`가 1 증가한다

**Given** Next.js 게시글 상세 페이지(`/posts/[id]`)에서
**When** 페이지가 로드되면
**Then** ImageSlider가 상단에 전체 너비로 렌더링된다 (가로 스와이프, 인디케이터 점)
**And** 판매자 프로필과 MannerTempWidget이 표시된다
**And** 판매자 본인이면 "수정/삭제", 타인이면 "채팅하기" 버튼이 하단에 고정 표시된다

**Given** Flutter 게시글 상세 화면에서
**When** 화면이 로드되면
**Then** 동일한 레이아웃과 역할 분기 버튼이 표시된다

### Story 2.5: 게시글 수정 & 삭제

As a 로그인한 판매자,
I want to edit or delete my own posts,
So that I can keep my listings accurate or remove them when sold.

**Acceptance Criteria:**

**Given** 판매자 본인이
**When** `PATCH /api/v1/posts/{post_id}`로 수정 요청을 보내면
**Then** 제목·설명·사진·가격·거래 희망 장소가 업데이트되고 `updated_at`이 갱신된다

**Given** 타인이 수정 또는 삭제를 시도하면
**When** API를 호출하면
**Then** `{"detail": "권한이 없습니다.", "code": "FORBIDDEN"}` 403 에러가 반환된다

**Given** 판매자 본인이 `DELETE /api/v1/posts/{post_id}`를 호출하면
**When** 삭제 요청이 처리되면
**Then** Supabase Storage에서 연결된 이미지 파일이 먼저 삭제된다
**And** DB 레코드가 삭제되며 FK CASCADE로 `chat_messages`, `likes`도 삭제된다
**And** Next.js 또는 Flutter에서 확인 다이얼로그 확인 후 홈 피드로 이동한다

### Story 2.6: 게시글 찜 (관심 등록·해제)

As a 로그인한 회원,
I want to like or unlike posts,
So that I can save items I'm interested in and track them later.

**Acceptance Criteria:**

**Given** 로그인한 회원이
**When** `POST /api/v1/posts/{post_id}/like`를 호출하면
**Then** `likes` 테이블에 레코드가 추가되고 `like_count`가 1 증가한다
**And** 이미 찜한 게시글에 다시 호출하면 찜이 해제되고 `like_count`가 1 감소한다 (토글)

**Given** 비로그인 사용자가 찜하기를 시도하면
**When** 하트 버튼을 탭하면
**Then** 로그인 페이지로 이동한다

**Given** Next.js 또는 Flutter 게시글 상세에서
**When** 하트 아이콘을 탭하면
**Then** 낙관적 UI로 즉시 아이콘 상태가 전환되고 `like_count`가 반영된다

---

## Epic 3: 1:1 채팅

구매자와 판매자가 게시글 기반 1:1 채팅방을 생성하고 실시간처럼 메시지를 주고받을 수 있다. 미읽음 배지와 낙관적 UI 포함.

### Story 3.1: 채팅방 생성 및 진입

As a 로그인한 구매자,
I want to start a chat with a seller by tapping "채팅하기" on a post,
So that I can negotiate and arrange a trade.

**Acceptance Criteria:**

**Given** `chat_messages` 테이블은 Story 1.1 초기 마이그레이션(AR-3)에서 이미 생성됨 (id, seller_email, buyer_email, post_id, message, is_read, sent_at + `idx_chat_messages_post_id_sent_at` 복합 인덱스)
**When** 로그인한 구매자가 `POST /api/v1/chats`를 호출하면 (`{post_id}` 포함)
**Then** 동일 (post_id, buyer_email) 조합의 채팅방이 없으면 새로 생성되고 room 정보가 반환된다
**And** 이미 존재하면 기존 room 정보가 반환된다 (중복 생성 방지)

**Given** 판매자 본인의 게시글에서 채팅하기를 시도하면
**When** `POST /api/v1/chats`를 호출하면
**Then** `{"detail": "본인 게시글에는 채팅할 수 없습니다.", "code": "SELF_CHAT_FORBIDDEN"}` 에러가 반환된다

**Given** Next.js 게시글 상세에서 "채팅하기" 버튼을 클릭하면
**When** 버튼이 클릭되면
**Then** 채팅방이 생성(또는 기존 방 반환)되고 채팅방 페이지(`/chat/[roomId]`)로 이동한다

**Given** Flutter 게시글 상세에서 하단 고정 "채팅하기" 버튼을 탭하면
**When** 버튼이 탭되면
**Then** 동일한 흐름으로 채팅방 화면으로 이동한다

### Story 3.2: 메시지 전송 및 수신 (폴링)

As a 채팅방 참여자,
I want to send messages and receive replies in near real-time,
So that I can communicate with the other party about the trade.

**Acceptance Criteria:**

**Given** 채팅방에 진입한 참여자가
**When** `POST /api/v1/chats/{room_id}/messages`로 메시지를 전송하면
**Then** 메시지가 DB에 저장되고 저장된 메시지 데이터가 반환된다

**Given** 클라이언트가 채팅방에 진입한 상태에서
**When** `GET /api/v1/chats/{room_id}/messages?after={last_message_id}`를 2500ms마다 호출하면
**Then** last_message_id 이후의 신규 메시지 배열이 반환된다 (없으면 빈 배열)
**And** 폴링 간격은 2500ms로 설정되어 SM-C1(1초 미만 금지)을 준수한다

**Given** Next.js 또는 Flutter 채팅방에서 메시지를 전송하면
**When** 전송 버튼을 탭하면
**Then** 낙관적 UI로 즉시 오른쪽 ChatBubble이 노출된다 ("전송 중" 아이콘 표시)
**And** 폴링으로 서버 확인 후 "전송 중" 아이콘이 제거된다

**Given** 전송 실패 시
**When** API 호출이 실패하면
**Then** ChatBubble에 에러 상태가 표시된다

### Story 3.3: 채팅 목록 조회

As a 로그인한 회원,
I want to see a list of all my chat rooms with key context,
So that I can quickly find and resume any conversation.

**Acceptance Criteria:**

**Given** 로그인한 회원이
**When** `GET /api/v1/chats`를 호출하면
**Then** 내가 참여한 채팅방 목록이 최근 메시지 기준 내림차순으로 반환된다
**And** 각 항목에 `room_id, post_thumbnail, opponent_name, last_message, last_sent_at, unread_count`가 포함된다

**Given** Next.js 채팅 탭(`/chat`)에서
**When** 페이지가 로드되면
**Then** ChatListTile 목록이 렌더링된다 (게시글 썸네일·상대방 이름·마지막 메시지·경과시간)
**And** 경과 시간은 클라이언트에서 계산한다 (방금 전/N분 전/N시간 전/N일 전)

**Given** Flutter 채팅 탭에서
**When** 탭에 진입하면
**Then** 동일한 ChatListTile 위젯 목록이 표시된다

### Story 3.4: 미읽음 배지

As a 로그인한 회원,
I want to see a badge on the chat tab showing how many chat rooms have unread messages,
So that I never miss a new message.

**Acceptance Criteria:**

**Given** 새 메시지가 수신되었으나 해당 채팅방에 미진입한 상태에서
**When** `GET /api/v1/chats/unread-count`를 호출하면
**Then** 미읽음 채팅방 수(`count`)가 반환된다 (개별 메시지 수가 아닌 채팅방 수 기준)

**Given** 클라이언트가 채팅방 밖에 있을 때
**When** 2500ms 폴링이 실행되면
**Then** 미읽음 수가 갱신되어 채팅 탭 배지(+N)가 업데이트된다

**Given** 채팅방에 진입하면
**When** `PATCH /api/v1/chats/{room_id}/read`를 호출하면
**Then** 해당 채팅방의 모든 메시지 `is_read`가 `true`로 업데이트된다
**And** 미읽음 배지 수치가 감소한다

**Given** 미읽음 채팅방이 없으면
**When** 채팅 탭이 표시되면
**Then** 배지가 표시되지 않는다

---

## Epic 4: 거래 완료 & 후기·매너온도

판매자가 거래 상태를 변경하고 구매자를 확정하며, 양측이 후기를 작성해 매너온도를 쌓는 거래 신뢰 시스템 완성.

### Story 4.1: 거래 상태 변경

As a 판매자,
I want to update the status of my post between 판매중, 예약중, and 거래완료,
So that buyers can see the current availability of my item.

**Acceptance Criteria:**

**Given** 판매자 본인이
**When** `PATCH /api/v1/posts/{post_id}/status`를 호출하면 (`{status: '예약중'|'판매중'}`)
**Then** 게시글 상태가 변경되고 변경된 게시글 데이터가 반환된다
**And** 상태 변경이 즉시 홈 피드의 StatusBadge에 반영된다

**Given** 타인이 상태 변경을 시도하면
**When** API를 호출하면
**Then** 403 `FORBIDDEN` 에러가 반환된다

**Given** Next.js 게시글 상세 또는 나의 당근 판매관리에서
**When** 상태 변경 버튼을 클릭하면
**Then** 새 상태를 선택할 수 있고 즉시 반영된다

**Given** Flutter에서도
**When** 동일한 상태 변경 UI를 사용하면
**Then** 동일하게 동작한다

### Story 4.2: 구매자 확정 & 거래완료 플로우

As a 판매자,
I want to mark a trade as complete and confirm the buyer,
So that the transaction is officially recorded and both parties can leave reviews.

**Acceptance Criteria:**

**Given** 판매자가 거래완료를 선택하면
**When** TradeCompleteSheet가 열리면
**Then** 현재 채팅 중인 구매자 목록이 표시된다

**Given** 판매자가 구매자를 선택하고 확정하면
**When** `PATCH /api/v1/posts/{post_id}/complete`를 호출하면 (`{buyer_email}`)
**Then** 게시글 `status`가 `거래완료`, `buyer_email`이 저장된다
**And** 거래완료 체크 애니메이션(1초)이 표시된다
**And** 후기 작성 CTA가 자동으로 노출된다

**Given** 거래완료로 변경된 게시글에 상태 변경을 다시 시도하면
**When** `PATCH /api/v1/posts/{post_id}/status`를 호출하면
**Then** `{"detail": "거래완료된 게시글은 상태를 변경할 수 없습니다.", "code": "TRADE_ALREADY_COMPLETED"}` 에러가 반환된다

### Story 4.3: 후기 작성 & 매너온도 반영

As a 거래 완료된 판매자 또는 구매자,
I want to leave a review for the other party,
So that the community can trust each other's manner temperature score.

**Acceptance Criteria:**

**Given** `reviews` 테이블은 Story 1.1 초기 마이그레이션(AR-3)에서 이미 생성됨 (id, post_id, writer_email, target_email, is_positive, tags[], comment, created_at)
**When** 거래 확정된 양측이 `POST /api/v1/reviews`를 호출하면
**Then** 후기가 저장되고 target_email의 `manner_temp`가 즉시 업데이트된다 (긍정 +1℃, 부정 -1℃, 범위 0~99℃)

**Given** 동일 거래에 이미 후기를 작성한 회원이 다시 시도하면
**When** `POST /api/v1/reviews`를 호출하면
**Then** `{"detail": "이미 후기를 작성했습니다.", "code": "REVIEW_ALREADY_SUBMITTED"}` 에러가 반환된다

**Given** 거래완료 후 후기 작성 CTA에서
**When** 긍정/부정을 선택하고 태그와 코멘트를 입력 후 제출하면
**Then** 성공 토스트와 함께 업데이트된 매너온도가 MannerTempWidget에 반영된다

---

## Epic 5: 나의 당근 (마이페이지)

회원이 자신의 판매관리·구매내역·관심목록을 한 곳에서 확인하고 관리할 수 있다.

### Story 5.1: 판매관리

As a 판매자,
I want to see all my posts filtered by status,
So that I can track and manage my active and completed listings.

**Acceptance Criteria:**

**Given** 로그인한 회원이
**When** `GET /api/v1/users/me/posts?status={판매중|예약중|거래완료}`를 호출하면
**Then** 해당 상태의 내 게시글 목록이 반환된다
**And** status 파라미터 없이 호출하면 전체 내 게시글이 반환된다

**Given** Next.js 나의 당근 판매관리 섹션에서
**When** 상태 필터 탭을 선택하면
**Then** 해당 상태의 게시글 목록이 표시되고 각 게시글에서 상태 변경 버튼에 접근할 수 있다

**Given** Flutter 나의당근 탭 판매관리 섹션에서
**When** 동일한 필터를 사용하면
**Then** 동일하게 동작한다

### Story 5.2: 구매내역

As a 구매자,
I want to see a list of trades where I was confirmed as the buyer,
So that I can review my purchase history.

**Acceptance Criteria:**

**Given** 로그인한 회원이
**When** `GET /api/v1/users/me/purchases`를 호출하면
**Then** `buyer_email = me`인 거래완료 게시글 목록이 반환된다
**And** 각 항목에 `title, photos[0], price, updated_at`이 포함된다

**Given** Next.js 또는 Flutter 구매내역 섹션에서
**When** 섹션에 진입하면
**Then** 게시글 제목·대표 사진·가격·거래완료 날짜가 표시된다

### Story 5.3: 관심목록

As a 회원,
I want to see all posts I've liked,
So that I can revisit items I was interested in.

**Acceptance Criteria:**

**Given** 로그인한 회원이
**When** `GET /api/v1/users/me/likes`를 호출하면
**Then** 내가 찜한 게시글 목록이 반환된다
**And** 삭제된 게시글은 FK CASCADE로 `likes`에서도 자동 제거되어 목록에 노출되지 않는다

**Given** Next.js 또는 Flutter 관심목록 섹션에서
**When** 섹션에 진입하면
**Then** 찜한 게시글이 PostCard 형식으로 표시된다
**And** 목록이 비어 있으면 빈 상태 안내가 표시된다

---

## Epic 6: 관리자 웹

관리자가 전용 웹에서 가입·로그인하고, 회원 계정 관리·게시글 관리·채팅 내역 열람을 수행할 수 있다.

### Story 6.1: 관리자 가입 & 로그인

As a 관리자,
I want to register and log in through the dedicated admin web,
So that I can access the admin dashboard to manage the service.

**Acceptance Criteria:**

**Given** carrot-admin 전용 웹 URL에서
**When** 이메일·비밀번호로 `POST /api/v1/admin/register`를 호출하면
**Then** 계정이 `role: admin`으로 저장되고 JWT가 반환된다

**Given** 관리자 계정으로 `POST /api/v1/auth/login`을 호출하면
**When** 로그인이 성공하면
**Then** JWT가 반환되고 carrot-admin 대시보드로 이동한다

**Given** `role: user`인 일반 계정으로 carrot-admin에 로그인을 시도하면
**When** 로그인 요청이 처리되면
**Then** `{"detail": "관리자 권한이 없습니다.", "code": "ADMIN_REQUIRED"}` 에러가 반환된다

**Given** carrot-admin의 모든 페이지에서
**When** 비로그인 또는 비관리자 상태로 접근하면
**Then** 로그인 페이지로 리다이렉트된다

**Given** 로그인 성공 후
**When** 대시보드가 로드되면
**Then** 사이드바에 회원 관리 / 거래 관리 / 채팅 관리 3개 메뉴가 표시된다

### Story 6.2: 회원 관리

As a 관리자,
I want to view all users and activate or deactivate their accounts,
So that I can control access and handle problematic users.

**Acceptance Criteria:**

**Given** 관리자가
**When** `GET /api/v1/admin/users`를 호출하면
**Then** 전체 회원 목록이 `{items: [...], total: N}` 형식으로 반환된다
**And** 각 항목에 `email, created_at, manner_temp, post_count, is_active`가 포함된다

**Given** 관리자가 특정 회원을 비활성화하면
**When** `PATCH /api/v1/admin/users/{email}/status`를 호출하면 (`{is_active: false}`)
**Then** 해당 회원의 `is_active`가 `false`로 변경된다
**And** 비활성화된 회원이 로그인을 시도하면 `ACCOUNT_INACTIVE` 에러가 반환된다

**Given** carrot-admin 회원 관리 페이지에서
**When** 페이지가 로드되면
**Then** shadcn DataTable로 회원 목록이 표시된다
**And** 활성화/비활성화 버튼 클릭 후 즉시 "완료" 토스트가 표시된다

### Story 6.3: 거래 관리 (게시글 관리)

As a 관리자,
I want to view all posts with status filters and force-delete problematic posts,
So that I can maintain service quality.

**Acceptance Criteria:**

**Given** 관리자가
**When** `GET /api/v1/admin/posts?status={판매중|예약중|거래완료}`를 호출하면
**Then** 필터에 해당하는 전체 게시글 목록이 반환된다
**And** status 파라미터 없이 호출하면 전체 게시글이 반환된다

**Given** 관리자가 `DELETE /api/v1/admin/posts/{post_id}`를 호출하면
**When** 삭제 요청이 처리되면
**Then** Supabase Storage 이미지 파일이 먼저 삭제된 후 DB 레코드가 삭제된다
**And** 일반 사용자 JWT로 이 엔드포인트를 호출하면 403이 반환된다

**Given** carrot-admin 거래 관리 페이지에서
**When** 상태 필터 탭을 선택하면
**Then** DataTable이 필터링된 결과를 표시하고 강제 삭제 버튼이 각 행에 제공된다

### Story 6.4: 채팅 관리

As a 관리자,
I want to view all chat rooms and read message history,
So that I can monitor communications and investigate disputes.

**Acceptance Criteria:**

**Given** 관리자가
**When** `GET /api/v1/admin/chats`를 호출하면
**Then** 전체 채팅방 목록이 반환된다
**And** 각 항목에 `room_id, seller_email, buyer_email, post_title, message_count, last_message_at`이 포함된다

**Given** 관리자가 특정 채팅방을 선택하면
**When** `GET /api/v1/admin/chats/{room_id}/messages`를 호출하면
**Then** 해당 채팅방의 전체 메시지 내역이 반환된다

**Given** carrot-admin 채팅 관리 페이지에서
**When** DataTable에서 특정 행을 클릭하면
**Then** 해당 채팅방의 메시지 내역이 열람된다

### Story 6.5: Railway 배포 설정

As a developer,
I want all three services deployed to Railway as independent services,
So that the application is accessible for portfolio demonstration.

**Acceptance Criteria:**

**Given** carrot-api, carrot-web, carrot-admin 각각 Railway 서비스로 배포하면
**When** 배포가 완료되면
**Then** 각 서비스가 독립적인 URL로 접근 가능하다

**Given** carrot-api 배포 시 `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`, `JWT_SECRET` 환경 변수가 설정되면
**When** 서버가 기동되면
**Then** Alembic 마이그레이션이 실행되고 FastAPI가 정상 응답한다

**Given** carrot-web 및 carrot-admin 배포 시 `NEXT_PUBLIC_API_URL`이 carrot-api Railway URL로 설정되면
**When** 빌드가 완료되면
**Then** 배포된 URL에서 서비스가 CORS 에러 없이 정상 동작한다
