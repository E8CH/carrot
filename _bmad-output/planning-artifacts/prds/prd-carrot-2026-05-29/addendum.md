# Addendum — carrot PRD

> PRD 본문에 담기엔 구현 수준이 깊은 기술 세부사항, 검토된 대안, DB 설계 등을 기록한다.

---

## 기술 스택 의사결정 (기술 리서치 이월)

| 영역 | 결정 | 근거 |
|------|------|------|
| 채팅 | DB 폴링 (REST GET, 2~3초) | 구현 단순, Phase 2 마이그레이션 부담 없음 |
| 인증 | Supabase Auth JWT 발급 + FastAPI JWT 검증 | Flutter·Next.js 공용 |
| 이미지 업로드 | Supabase Storage Presigned URL | 서버 부하 없는 직접 업로드 |
| DB Phase 1 | Supabase PostgreSQL | BaaS 기반 빠른 개발 |
| DB Phase 2 | Railway PostgreSQL | Supabase 의존성 제거 |

---

## DB 스키마 (idea.md 기반, 보완 포함)

```sql
-- 회원
회원 (
  email        VARCHAR PK,
  password     VARCHAR,        -- bcrypt 해시
  address      VARCHAR,        -- 프로필 표시용 텍스트
  phone        VARCHAR,
  role         VARCHAR DEFAULT 'user',  -- 'user' | 'admin'
  is_active    BOOLEAN DEFAULT TRUE,
  manner_temp  DECIMAL(4,1) DEFAULT 36.5,
  created_at   TIMESTAMP
)

-- 게시글
게시글 (
  id            SERIAL PK,
  seller_email  VARCHAR FK → 회원.email,
  buyer_email   VARCHAR FK → 회원.email,  -- 거래완료 시 확정
  photos        TEXT[],                   -- Supabase Storage URL 배열
  title         VARCHAR,
  description   TEXT,
  price         INTEGER,                  -- NULL이면 나눔
  is_free       BOOLEAN DEFAULT FALSE,
  trade_place   VARCHAR,                  -- 거래 희망 장소 (텍스트)
  status        VARCHAR DEFAULT '판매중', -- '판매중'|'예약중'|'거래완료'
  view_count    INTEGER DEFAULT 0,
  created_at    TIMESTAMP,
  updated_at    TIMESTAMP
)

-- 채팅 (post_id 추가 확정 — Q1 해소)
채팅 (
  id            SERIAL PK,
  seller_email  VARCHAR FK → 회원.email,
  buyer_email   VARCHAR FK → 회원.email,
  post_id       INTEGER FK → 게시글.id,  -- 채팅방 식별 키 (seller+buyer+post 조합)
  message       TEXT,
  is_read       BOOLEAN DEFAULT FALSE,   -- 미읽음 배지(FR-14a) 구현용
  sent_at       TIMESTAMP
)

-- 후기 (idea.md 미포함 → 기능 요건에서 도출)
후기 (
  id            SERIAL PK,
  post_id       INTEGER FK → 게시글.id,
  writer_email  VARCHAR FK → 회원.email,
  target_email  VARCHAR FK → 회원.email,
  is_positive   BOOLEAN,
  tags          TEXT[],
  comment       TEXT,
  created_at    TIMESTAMP
)

-- 관심 (찜)
관심 (
  id            SERIAL PK,
  user_email    VARCHAR FK → 회원.email,
  post_id       INTEGER FK → 게시글.id,
  created_at    TIMESTAMP,
  UNIQUE (user_email, post_id)
)
```

---

## 채팅 폴링 흐름

```
[클라이언트] --GET /chats/{room_id}/messages?after={last_message_id}--> [FastAPI]
                                                                               |
                                                                          PostgreSQL
                                                                          (신규 메시지 조회)
[클라이언트] <-- 신규 메시지 배열 (빈 배열이면 변화 없음) --
2~3초 후 반복
```

---

## 매너온도 계산 (가정, 확정 전)

- 초기값: 36.5℃
- 긍정 후기 1건: +1.0℃
- 부정 후기 1건: -1.0℃
- 최솟값: 0℃, 최댓값: 99℃ (당근마켓 UI 스크린샷 기준)

---

## 검토된 대안

### 채팅: Supabase Realtime vs. DB 폴링

| | Supabase Realtime | DB 폴링 (채택) |
|--|--|--|
| 지연시간 | 200ms 이하 | 2~3초 |
| 구현 복잡도 | 중간 | 낮음 |
| Phase 2 호환 | 재구현 필요 | 그대로 사용 가능 |
| 결론 | 미채택 | **채택** |
