# Deferred Work

## Deferred from: code review of 6-5-railway-배포-설정 (2026-05-30)

- DATABASE_URL +asyncpg 접두사 필요 [carrot-api] — Railway 환경변수 설정 시 `postgresql+asyncpg://...` 형식 사용 필요; 운영 가이드에 명시
- uv 버전 미고정 [carrot-api/Dockerfile] — `pip install uv==X.Y.Z`로 고정 시 재현성 향상; 실서비스 전환 시 처리
- 비루트 사용자 없음 [carrot-api/Dockerfile] — `RUN useradd -m app && USER app` 추가; 보안 강화 포트폴리오 이후 처리
- NEXT_PUBLIC_API_URL 미설정 시 빈 문자열 [carrot-web/admin Dockerfile] — Railway 빌드 파이프라인에서 `--build-arg NEXT_PUBLIC_API_URL=...` 반드시 설정; ops 절차로 관리

## Deferred from: code review of 6-4-채팅-관리 (2026-05-30)

- 채팅방/메시지 목록 페이지네이션 없음 [admin/repository.py] — 포트폴리오 admin view; 실서비스 시 LIMIT/OFFSET 추가
- INNER JOIN으로 삭제된 게시글 채팅방 소실 [admin/repository.py] — CASCADE 설계 의도; 채팅 기록 보존 필요 시 LEFT JOIN + soft-delete 도입
- 비존재 room_id 200 OK 반환 [admin/router.py] — 포트폴리오; 실서비스 시 room 존재 검증 후 404 반환
- 관리자 액션 로깅 없음 [admin/router.py] — 포트폴리오 범위 외; 실서비스 시 audit log 미들웨어 추가

## Deferred from: code review of 6-3-거래-관리-게시글-관리 (2026-05-30)

- 페이지네이션 없음 [admin/repository.py] — 스토리 스펙에서 admin view no-pagination 명시; 서비스 규모 증가 시 LIMIT/OFFSET 추가
- 동기식 Supabase Storage 호출 [admin/router.py] — posts/router.py 기존 패턴; asyncio.to_thread() 래핑은 전체 Supabase 호출 패턴 리팩토링 시 처리
- 동시 삭제 레이스 컨디션 [admin/router.py] — 포트폴리오/단일 관리자 환경; 멀티 관리자 도입 시 SELECT FOR UPDATE 패턴 적용
- Storage 부분 실패 응답 미확인 [admin/router.py] — orphan files 허용 (포트폴리오); 실서비스 전환 시 remove() 응답 body 파싱 및 경고 로그 추가

## Deferred from: code review of 5-1-판매관리 (2026-05-30)

- get_my_posts COUNT 비효율 — `len(rows)` Python-side 카운트, 대규모 트래픽 시 COUNT(*) 서브쿼리로 교체 필요

## Deferred from: code review of 4-3-후기-작성-매너온도-반영 (2026-05-30)

- Web MannerTempWidget 갱신 — router.refresh() 필요, 앱 전역 Next.js 캐시 영향 범위 큼, 별도 상태관리 패턴 도입 시 처리
- buyer_email=None 엣지케이스 — Story 4-2 completePost 엔드포인트에서 buyer_email 필수 설정됨, 발생 불가 시나리오

## Deferred from: code review of 4-2-구매자-확정-거래완료-플로우 (2026-05-30)

- 동시 PATCH complete 경쟁 조건 — non-atomic read-write, SELECT FOR UPDATE 필요 (포트폴리오 범위 초과)
- 삭제된 계정의 buyer_email이 구매자 목록에 노출 — FK 아키텍처 이슈, 사용자 삭제 플로우와 함께 처리
- chat_count/like_count 하드코딩 0 반환 — create_post/update_post/change_status와 동일한 기존 패턴
- PostDetailResponse에 buyer_email 미포함 — 설계 결정, 클라이언트가 invalidateQueries로 재조회함

## Deferred from: code review of 4-1-거래-상태-변경 (2026-05-30)

- chat_count/like_count 하드코딩 0 반환 — create_post/update_post와 동일한 기존 패턴, 향후 실제 집계로 교체 고려
- JWT sub claim 이메일 형식 검증 없음 — 전체 라우터 공통 패턴, Story 1.x 설계 검토 필요
- Flutter PostsRepository 인라인 인스턴스화 — 전체 화면 공통 패턴, DI 리팩토링 시 함께 처리
- 동시 PATCH 경쟁 조건 (행 잠금 없음) — 포트폴리오 범위 초과, SELECT FOR UPDATE 필요
- 상태 변경 후 _loadPost 중 토큰 만료 — 토큰 갱신 미들웨어와 함께 처리 필요

## Deferred from: code review of 2-2-게시글-작성-이미지-업로드 (2026-05-30)

- 업로드 성공 후 DB commit 실패 시 Supabase Storage 고아 파일 — distributed transaction 문제, 보상 트랜잭션 또는 정기 cleanup job 필요
- like_count/chat_count 상관 서브쿼리 N+1 — Story 2.1 pre-existing, LEFT JOIN + GROUP BY로 교체 필요
- seller_email path sanitization (@ 등 특수문자) — Storage path에 email 특수문자 URL 인코딩 처리 필요
- JWT sub claim이 email이라는 가정 — Supabase가 UUID를 sub로 발급하는 경우 처리 필요, Story 1.x 설계 검토
- /upload-url rate limiting 없음 — 인증된 사용자의 presigned URL 남용 방지, API gateway 또는 미들웨어 레벨 처리
- CORS production domain 미등록 — 배포 시 `allow_origins`에 production 도메인 추가 필요
- Flutter sequential upload (병렬 아님) — 10장 업로드 시 성능 저하, Future.wait()로 병렬화 고려
- 부분 업로드 실패 시 재시도 중복 파일 — 실패한 파일만 재업로드하는 idempotent 로직 필요
- price 서버사이드 상한 없음 — PostgreSQL INTEGER 오버플로우 방지용 max_length 또는 validator 추가
- _supabase 모듈 로드 시 동기 클라이언트 생성 — FastAPI lifespan 이벤트로 이동 또는 async 클라이언트 전환 고려
- photo URLs 형식 검증 없음 — 클라이언트 제공 URL XSS/SSRF 가능성, 허용 도메인 whitelist 또는 URL 검증 추가
