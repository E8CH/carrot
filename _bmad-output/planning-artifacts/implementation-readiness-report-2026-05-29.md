---
stepsCompleted: ["step-01-document-discovery", "step-02-prd-analysis", "step-03-epic-coverage-validation", "step-04-ux-alignment", "step-05-epic-quality-review", "step-06-final-assessment"]
status: complete
documentsInventoried:
  prd: "_bmad-output/planning-artifacts/prds/prd-carrot-2026-05-29/prd.md"
  prdAddendum: "_bmad-output/planning-artifacts/prds/prd-carrot-2026-05-29/addendum.md"
  architecture: "_bmad-output/planning-artifacts/architecture.md"
  epics: "_bmad-output/planning-artifacts/epics.md"
  uxDesign: "_bmad-output/planning-artifacts/ux-design-specification.md"
---

# Implementation Readiness Assessment Report

**Date:** 2026-05-29
**Project:** carrot

---

## PRD 분석

### 기능 요건 (Functional Requirements)

| ID | 제목 | 설명 |
|----|------|------|
| FR-1 | 회원가입 | 이메일·비밀번호·주소·연락처 입력으로 계정 생성 |
| FR-2 | 로그인 | 이메일·비밀번호 인증 후 JWT 발급 |
| FR-3 | 로그아웃 | 클라이언트에서 JWT 제거 |
| FR-4 | 회원 프로필 조회 | 이메일·주소·연락처·매너온도 조회 |
| FR-5 | 게시글 작성 | 사진·제목·설명·가격(또는 나눔)·거래 희망 장소 입력으로 게시글 등록 |
| FR-6 | 임시저장 | 게시글 작성 중 임시저장 (계정당 1개) |
| FR-7 | 게시글 목록 조회 | 전체 게시글 최신순 목록 (비로그인 포함, 20개씩) |
| FR-8 | 게시글 상세 조회 | 이미지 슬라이더·판매자 프로필·매너온도·제목·가격·설명·상태·채팅/관심/조회 수 |
| FR-9 | 게시글 수정 | 판매자 본인 게시글 수정 |
| FR-10 | 게시글 삭제 | 판매자 본인 게시글 삭제 (연결 채팅 메시지도 삭제) |
| FR-11 | 게시글 찜 | 관심 등록/해제, 나의 당근 관심목록 연동 |
| FR-12 | 채팅방 생성 | 구매자가 게시글 상세에서 채팅하기 클릭 시 1:1 채팅방 생성 |
| FR-13 | 메시지 전송 및 수신 | 텍스트 메시지 전송·수신 (DB 폴링 2~3초) |
| FR-14 | 채팅 목록 조회 | 참여 중 채팅방 목록 (게시글 썸네일, 상대방 이름, 마지막 메시지, 경과 시간) |
| FR-14a | 채팅 탭 미읽음 배지 | 미읽음 채팅방 수 배지(+N), 2~3초 폴링 동기화 |
| FR-15 | 거래 상태 변경 | 판매자가 판매중/예약중/거래완료로 상태 변경 |
| FR-16 | 구매자 확정 | 거래완료 시 채팅 중인 구매자 목록에서 선택·확정 |
| FR-17 | 후기 작성 | 거래완료 후 판매자↔구매자 상호 후기 1회 작성 |
| FR-18 | 매너온도 표시 | 프로필·게시글 상세에 매너온도 표시 (초기 36.5℃) |
| FR-19 | 판매관리 | 본인 등록 게시글 상태별 목록 조회 |
| FR-20 | 구매내역 | 구매자로 확정된 거래완료 게시글 목록 조회 |
| FR-21 | 관심목록 | 찜한 게시글 목록 조회 (삭제된 게시글 자동 제거) |
| FR-22 | 관리자 회원가입 | 관리자 전용 웹에서 관리자 계정 생성 (role: admin) |
| FR-23 | 관리자 로그인 | 관리자 이메일·비밀번호 로그인, 대시보드 이동 |
| FR-24 | 회원 관리 | 전체 회원 목록 조회 및 활성화/비활성화 |
| FR-25 | 거래 관리 | 전체 게시글 목록·상태 조회, 강제 삭제 |
| FR-26 | 채팅 관리 | 전체 채팅방 목록·메시지 열람 |

**총 FR 수: 27개** (FR-1~FR-26 + FR-14a)

### 비기능 요건 (Non-Functional Requirements)

| ID | 영역 | 내용 |
|----|------|------|
| NFR-1 | 인증 | JWT Bearer 토큰 검증, 만료 시 401 반환 |
| NFR-2 | 이미지 업로드 | Supabase Storage Presigned URL, 이미지당 최대 5MB |
| NFR-3 | 채팅 폴링 | 클라이언트 2~3초 간격 GET 폴링 |
| NFR-4 | CORS | 사용자 웹·관리자 웹·Flutter 앱 도메인 허용 |
| NFR-5 | 응답 속도 | 게시글 목록 API p95 2초 이내 |

**총 NFR 수: 5개**

### 추가 요건 및 제약

- **플랫폼:** Next.js(사용자 웹) + Next.js(관리자 웹) + Flutter(모바일) + FastAPI(백엔드)
- **DB 전략:** Phase 1 Supabase PostgreSQL → Phase 2 Railway PostgreSQL 마이그레이션
- **매너온도 공식:** 36.5℃ 기준, ±1℃/후기, 범위 0~99℃
- **Non-Goal:** 위치 기반, 인앱 결제, 커뮤니티, 소셜 로그인, 푸시 알림, 신고 처리 워크플로우

### PRD 완성도 평가

PRD는 27개 기능 요건을 명확한 검증 조건과 함께 정의하고 있으며, 가정 사항(17개)이 명시적으로 인덱싱되어 있다. 비기능 요건은 간결하게 정의되어 있다. 전반적으로 MVP 범위가 명확하다.

---

## 에픽 커버리지 검증

### FR 커버리지 매트릭스

| FR | PRD 요건 | 에픽/스토리 | 상태 |
|----|---------|------------|------|
| FR-1 | 회원가입 | Epic 1 / Story 1.2 | ✅ 커버됨 |
| FR-2 | 로그인 | Epic 1 / Story 1.3 | ✅ 커버됨 |
| FR-3 | 로그아웃 | Epic 1 / Story 1.3 | ✅ 커버됨 |
| FR-4 | 회원 프로필 조회 | Epic 1 / Story 1.4 | ✅ 커버됨 |
| FR-5 | 게시글 작성 | Epic 2 / Story 2.2 | ✅ 커버됨 |
| FR-6 | 임시저장 | Epic 2 / Story 2.3 | ✅ 커버됨 |
| FR-7 | 게시글 목록 조회 (홈 피드) | Epic 2 / Story 2.1 | ✅ 커버됨 |
| FR-8 | 게시글 상세 조회 | Epic 2 / Story 2.4 | ✅ 커버됨 |
| FR-9 | 게시글 수정 | Epic 2 / Story 2.5 | ✅ 커버됨 |
| FR-10 | 게시글 삭제 | Epic 2 / Story 2.5 | ✅ 커버됨 |
| FR-11 | 게시글 찜 (관심) | Epic 2 / Story 2.6 | ✅ 커버됨 |
| FR-12 | 채팅방 생성 | Epic 3 / Story 3.1 | ✅ 커버됨 |
| FR-13 | 메시지 전송 및 수신 | Epic 3 / Story 3.2 | ✅ 커버됨 |
| FR-14 | 채팅 목록 조회 | Epic 3 / Story 3.3 | ✅ 커버됨 |
| FR-14a | 채팅 탭 미읽음 배지 | Epic 3 / Story 3.4 | ✅ 커버됨 |
| FR-15 | 거래 상태 변경 | Epic 4 / Story 4.1 | ✅ 커버됨 |
| FR-16 | 구매자 확정 | Epic 4 / Story 4.2 | ✅ 커버됨 |
| FR-17 | 후기 작성 | Epic 4 / Story 4.3 | ✅ 커버됨 |
| FR-18 | 매너온도 표시 | Epic 4 / Story 4.3 | ✅ 커버됨 |
| FR-19 | 판매관리 | Epic 5 / Story 5.1 | ✅ 커버됨 |
| FR-20 | 구매내역 | Epic 5 / Story 5.2 | ✅ 커버됨 |
| FR-21 | 관심목록 | Epic 5 / Story 5.3 | ✅ 커버됨 |
| FR-22 | 관리자 회원가입 | Epic 6 / Story 6.1 | ✅ 커버됨 |
| FR-23 | 관리자 로그인 | Epic 6 / Story 6.1 | ✅ 커버됨 |
| FR-24 | 회원 관리 | Epic 6 / Story 6.2 | ✅ 커버됨 |
| FR-25 | 거래 관리 | Epic 6 / Story 6.3 | ✅ 커버됨 |
| FR-26 | 채팅 관리 | Epic 6 / Story 6.4 | ✅ 커버됨 |

### 누락된 요건

없음. 모든 FR이 에픽/스토리에서 커버됨.

### 커버리지 통계

- **PRD 총 FR 수:** 27개
- **에픽에서 커버된 FR 수:** 27개
- **커버리지:** 100%

---

## UX 정합성 검증

### UX 문서 상태

✅ **발견됨** — `ux-design-specification.md` (14단계 완료)

### UX ↔ PRD 정합성

| UX 요건 | PRD 연계 | 상태 |
|---------|---------|------|
| 하단 3탭 (홈/채팅/나의당근) | FR-7, FR-14, FR-19~21 | ✅ 정합 |
| PostCard (썸네일·제목·가격·상태배지·채팅수·관심수) | FR-7, FR-8 | ✅ 정합 |
| ImageSlider (게시글 상세 상단 전체 너비) | FR-8 | ✅ 정합 |
| 하단 고정 "채팅하기" CTA | FR-12 | ✅ 정합 |
| ChatListTile (썸네일·상대방·마지막메시지·경과시간) | FR-14 | ✅ 정합 |
| 미읽음 배지 (+N) | FR-14a | ✅ 정합 |
| 낙관적 UI 메시지 전송 | FR-13 | ✅ 정합 |
| TradeCompleteSheet (거래완료→구매자→후기CTA) | FR-15, FR-16, FR-17 | ✅ 정합 |
| MannerTempWidget (색상 그라데이션) | FR-18 | ✅ 정합 |
| FAB (글쓰기, 모바일 우하단) | FR-5 | ✅ 정합 |
| StatusBadge (판매중/예약중/거래완료) | FR-7, FR-8, FR-15 | ✅ 정합 |
| 관리자 DataTable + 사이드바 | FR-22~26 | ✅ 정합 |

### UX ↔ 아키텍처 정합성

| UX 요건 | 아키텍처 지원 | 상태 |
|---------|------------|------|
| Tailwind CSS + shadcn/ui (Next.js) | AR-8, AR-9 / 에픽에서 확인 | ✅ 정합 |
| Material 3 + ThemeData (Flutter) | AR-10 / 에픽에서 확인 | ✅ 정합 |
| TanStack Query (낙관적 UI, 캐싱) | AR-9 / Story 1.1에서 확인 | ✅ 정합 |
| Riverpod (Flutter 상태 관리) | AR-10 / Story 1.1에서 확인 | ✅ 정합 |
| 폴링 2500ms (낙관적 UI 연동) | NFR-3, SM-C1 준수 / Story 3.2 | ✅ 정합 |
| Supabase Storage Presigned URL (이미지 업로드) | NFR-2, AR-5 / Story 2.2 | ✅ 정합 |

### 경고

없음. UX ↔ PRD, UX ↔ 아키텍처 모두 완전 정합.

---

## 에픽 품질 검토

### 에픽 구조 검증 — 사용자 가치 포커스

| 에픽 | 제목 | 사용자 가치 | 판정 |
|------|------|-----------|------|
| 1 | 플랫폼 초기화 & 회원 인증 | 가입·로그인·프로필 조회 (greenfield 초기화 포함, 허용) | ✅ |
| 2 | 게시글 등록 & 피드 탐색 | 물품 등록·탐색·찜 전체 | ✅ |
| 3 | 1:1 채팅 | 채팅방 생성·메시지·목록·배지 | ✅ |
| 4 | 거래 완료 & 후기·매너온도 | 거래 확정·후기·신뢰도 시스템 | ✅ |
| 5 | 나의 당근 (마이페이지) | 판매관리·구매내역·관심목록 | ✅ |
| 6 | 관리자 웹 | 관리자 가입·로그인·회원/거래/채팅 관리 | ✅ |

### 에픽 독립성 검증

- Epic 1 → 독립 완결 ✅
- Epic 2 → Epic 1만 의존 ✅
- Epic 3 → Epic 1+2 의존 (채팅방에 게시글 필요) ✅
- Epic 4 → Epic 1+2+3 의존 (거래완료 시 채팅방 구매자 목록 참조) ✅ (순차적 의존, 순환 없음)
- Epic 5 → Epic 1+2+4 의존 (구매내역에 거래완료 필요) ✅
- Epic 6 → Epic 1 의존 (인증 시스템) ✅ (Epic 2~5 완료 후 구현 권장)

순환 의존: 없음 ✅

### 스토리 품질 평가

#### 🔴 Critical Violations

없음.

#### 🟠 Major Issues

**[M-1] 마이그레이션 전략 불일치** — Story 1.1 vs. 개별 스토리

- **위치:** Story 1.1 (AR-3 포함) + Story 2.1 + Story 3.1 + Story 4.3
- **문제:** Story 1.1이 AR-3("DB 스키마 생성 — users, posts, chats, reviews, likes 테이블 전체 + FK CASCADE")을 담당한다. 동시에 Story 2.1은 "posts, likes 테이블 마이그레이션이 포함된다", Story 3.1은 "chat_messages 테이블 마이그레이션이 완료된 상태에서", Story 4.3은 "reviews 테이블 마이그레이션이 완료된 상태에서"라고 명시해 두 가지 접근법이 충돌한다.
- **영향:** Story 1.1에서 AR-3 전체를 구현하면 이후 스토리의 마이그레이션 언급이 중복·무의미해진다. 반대로 JIT(필요 시점 생성) 방식을 따르면 AR-3 자체가 모순이 된다.
- **권장 조치:** Story 1.1에서 AR-3를 수정해 **users 테이블만 생성** 하도록 범위를 축소하고, posts+likes는 Story 2.1, chat_messages는 Story 3.1, reviews는 Story 4.3에서 각각 마이그레이션을 생성하는 JIT 방식을 채택한다.

#### 🟡 Minor Concerns

**[m-1] Story 1.1 범위 과대 (9개 플랫폼 초기화 항목)**
- 모노레포 구조, FastAPI/Next.js ×2/Flutter 초기화, 색상 토큰, Axios, TanStack Query, Riverpod를 단일 스토리에 포함.
- 특정 플랫폼 설정 실패 시 스토리 전체가 블로킹될 수 있다.
- **권장:** 현행 유지 가능 (greenfield 초기화의 특성상 허용). 단, Story 1.1 구현 시 플랫폼별로 커밋을 분리해 리뷰 용이하게 할 것.

**[m-2] 구매자 후기 진입 경로 미명시**
- Story 4.2에서 판매자 측 거래완료 후 "후기 작성 CTA가 자동으로 노출된다"는 명시되나, 구매자가 어떻게 후기 작성 화면에 도달하는지 AC에 미정의.
- FR-16("확정 후 양측에 후기 작성 알림 노출") 요건이 완전히 충족되지 않을 수 있다.
- **권장:** Story 4.3의 AC에 "구매자는 채팅방 또는 구매내역에서 후기 작성 CTA에 접근할 수 있다" 조건 추가.

**[m-3] Story 6.5 사용자 가치 미흡**
- Railway 배포 설정은 기술적 운영 작업으로 직접적 사용자 가치가 없다.
- 포트폴리오 시연 목적의 필수 요건이므로 제거는 부적절.
- **권장:** 스토리 설명에 "이 스토리는 포트폴리오 시연 접근성을 위한 배포 설정이다"를 명시.

### 베스트 프랙티스 준수 체크리스트

| 항목 | 상태 |
|------|------|
| 모든 에픽이 사용자 가치 전달 | ✅ |
| 에픽 독립성 유지 | ✅ |
| 스토리 적절한 크기 | ✅ (1.1 경계선) |
| 전방 의존성 없음 | ✅ |
| DB 테이블 필요 시점 생성 | 🟠 불일치 존재 (M-1) |
| 명확한 인수 조건 (Given/When/Then) | ✅ |
| FR 추적성 유지 | ✅ (커버리지 맵 완비) |

---

## 최종 평가 요약 및 권고

### 전체 구현 준비도 상태

> ## ✅ READY FOR IMPLEMENTATION
>
> 조건부 진행 가능 — 아래 M-1 이슈 해소 후 Phase 4 시작 권장 (Sprint Planning)

---

### 즉시 조치 필요 항목

#### [M-1] Story 1.1 마이그레이션 범위 조정 (권장, 필수는 아님)

현재 AR-3은 Story 1.1에서 모든 테이블(users·posts·chats·reviews·likes)을 일괄 생성하도록 정의되어 있으나, 개별 스토리의 Given 조건이 JIT 방식을 전제한다. 이 불일치를 해소하지 않으면 개발자가 혼란을 겪는다.

**선택지 A (권장):** `epics.md`의 AR-3을 수정해 Story 1.1에서 **users 테이블만** Alembic 마이그레이션으로 생성하고, 나머지는 각 스토리에서 JIT 생성.

**선택지 B:** AR-3 그대로 유지 (일괄 생성). 단, Story 2.1·3.1·4.3의 마이그레이션 언급을 "마이그레이션은 Story 1.1에서 이미 완료됨"으로 수정.

둘 중 하나를 선택해 epics.md에 반영하면 된다. **구현 자체를 막는 결함은 아니다.**

---

### 권장 다음 단계

1. **[선택] M-1 해소** — `epics.md` AR-3 범위 또는 개별 스토리 Given 조건을 일관되게 수정
2. **[선택] m-2 해소** — Story 4.3에 구매자 후기 진입 경로 AC 추가
3. **Phase 4 시작 — Sprint Planning** → `/bmad-sprint-planning`

---

### 최종 평가 메모

이번 평가에서 발견된 이슈:
- **🔴 Critical:** 0개
- **🟠 Major:** 1개 (마이그레이션 전략 불일치, 구현 전 해소 권장)
- **🟡 Minor:** 3개 (Story 1.1 범위, 구매자 후기 경로, Story 6.5 설명)

PRD 요건 27개 전부 에픽/스토리에 추적되고, UX ↔ PRD ↔ 아키텍처 정합성은 완전하다. 발견된 이슈는 구현을 차단할 수준이 아니며, Phase 4 진입에 문제 없다.

**평가일:** 2026-05-29 | **평가자:** Claude (BMad Implementation Readiness Check)
