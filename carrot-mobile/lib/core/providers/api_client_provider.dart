import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import 'token_provider.dart';

/// tokenProvider를 감시하여 토큰 변경 시 자동으로 새 ApiClient를 반환한다.
/// 이후 모든 Flutter 스토리에서 API 호출은 ref.read(apiClientProvider)로 획득한다.
final apiClientProvider = Provider<ApiClient>((ref) {
  final token = ref.watch(tokenProvider);
  return ApiClient(token: token);
});
