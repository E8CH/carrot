아래 기능을 포함한 크로스 플랫폼 서비스의 핵심 기능 구현을 하려고해.
최소 기능만 구현하려고해.
한국의 "당근"이라는 서비스의 핵심 기능과 유사해.

- 기능 범위
  - 판매자 : 가입 > 로그인 > 글쓰기 > 물품정보 작성 > 게시글에 저장 > 채팅 > 상태변경 (예약중 > 판매중 > 거래완료) > 구매자 후기 작성
  - 구매자 : 가입 > 로그인 > 게시글 열람 > 채팅 > 거래완료 > 판매자 후기 작성
  - 관리자: 가입 > 로그인 > 고객 관리 > 거래관리 , 채팅 관리

- 시연에 사용하는 기술 스택
  - 1. 사용자(고객/고수)용 반응형 웹 (Next.js)
  - 2. 관리자용 반응형 웹 (Next.js)
  - 3. 사용자(고객/고수)용 모바일 앱 (flutter)
  - 4. 통합 API (FastAPI)
  - 5. DB (Supabase, PostgreSQL)
  - 6. 배포 (Railway : 프론트엔드, 백엔드, PostgreSQL), 테스트 (expo go)

-DB 설계
회원 : e-mail(PK), password, 주소, 연락처
게시글 : increase number (PK), e-mail(회원:판매자), e-mail(회원:구매자), 사진, 글, 게시날짜(yyyyMMhhss.zzz), 상태(예약중,판매중,거래완료)
채팅 : increase number (PK), e-mail(회원:판매자), e-mail(회원:구매자), 메시지, 날짜(yyyyMMhhss.zzz)

-조건
회원은 판매자가 될 수도 있고 구매자가 될 수도 있다
채팅방에는 1:1 채팅만 가능하다. 만약 여러 구매자가 판매자에게 대화를 걸면 판매자는 여러 대화창이 생겨서 각각 1:1로 채팅한다.
상태변경은 판매자가 채팅방에서 설정변경을 통해 할 수 있다. 또한 동시에 판매자가 게시글에서 상태변경을 할 수도 있다.
"나의 당근"이라는 버튼을 누르면 각 회원은 판매관리, 구매내역을 확인 할 수 있다.


- 참고 사항
Supabase로 database 개발을 먼저 하고, PostgreSQL (Railway)로 마이그레이션하여 마무리.
[1단계: Supabase 기반의 개발 ] → [2단계: FastAPI 인프라 Railway PostgreSQL로 완전히 독립
Phase 1 (BaaS 기반): FastAPI와 Supabase(DB)를 연동해 빠른 기능 구현.
Phase 2 (인프라 독립): Supabase 의존성을 제거하고, Railway의 PostgreSQL로 DB 마이그레이션 및