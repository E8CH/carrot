class ApiEndpoints {
  // ⚠️ 플랫폼별 baseUrl 선택:
  //   Android 에뮬레이터 : 'http://10.0.2.2:8000'
  //   iOS 시뮬레이터     : 'http://localhost:8000'
  //   실기기 (로컬)      : 'http://<내 PC IP>:8000'  예) 'http://192.168.0.5:8000'
  //   Railway 배포 후    : 'https://carrot-api.up.railway.app'
  static const baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android 에뮬레이터 기본값
  );

  // Supabase 공개 스토리지 URL (--dart-define=SUPABASE_URL=https://xxx.supabase.co)
  static const supabaseUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: 'https://placeholder.supabase.co',
  );

  static const auth = '/api/v1/auth';
  static const authLogin = '/api/v1/auth/login';
  static const authRegister = '/api/v1/auth/register';

  static const posts = '/api/v1/posts/';
  static const postsUploadUrl = '/api/v1/posts/upload-url';
  static const postsDraft = '/api/v1/posts/draft';
  static String postDetail(int id) => '/api/v1/posts/$id';
  static String postLike(int id) => '/api/v1/posts/$id/like';
  static String postStatus(int id) => '/api/v1/posts/$id/status';
  static String postBuyers(int id) => '/api/v1/posts/$id/buyers';
  static String postComplete(int id) => '/api/v1/posts/$id/complete';

  static const chats = '/api/v1/chats/';
  static String chatMessages(String roomId) => '/api/v1/chats/$roomId/messages';
  static String chatRead(String roomId) => '/api/v1/chats/$roomId/read';
  static const chatsUnreadCount = '/api/v1/chats/unread-count';

  static const usersMe = '/api/v1/users/me';
  static const usersMePosts = '/api/v1/users/me/posts';
  static const usersMePurchases = '/api/v1/users/me/purchases';
  static const usersMeLikes = '/api/v1/users/me/likes';

  static const reviews = '/api/v1/reviews/';
}
