import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 메모리 상의 현재 JWT 토큰. null이면 비로그인.
final tokenProvider = StateProvider<String?>((ref) => null);

/// 앱 시작 시 SharedPreferences에서 저장된 토큰을 복원한다.
/// main.dart의 ConsumerWidget에서 watch하여 초기화를 트리거한다.
final tokenInitializerProvider = FutureProvider<void>((ref) async {
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('token');
  if (token != null) {
    ref.read(tokenProvider.notifier).state = token;
  }
});

/// 토큰을 저장하고 tokenProvider를 갱신하는 헬퍼 함수.
/// 디스크에 먼저 쓰고 성공 후 메모리를 갱신하여 상태 불일치를 방지한다.
Future<void> saveToken(WidgetRef ref, String token) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString('token', token); // 디스크 먼저 — 실패 시 메모리 변경 없음
  ref.read(tokenProvider.notifier).state = token;
}

/// 토큰을 삭제하고 tokenProvider를 초기화하는 헬퍼 함수.
/// 디스크에서 먼저 삭제하여 재시작 후 자동 로그인 방지.
Future<void> clearToken(WidgetRef ref) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.remove('token'); // 디스크 먼저
  ref.read(tokenProvider.notifier).state = null;
}
