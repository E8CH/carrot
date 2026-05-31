import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/providers/token_provider.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/presentation/login_screen.dart';
import 'shared/widgets/main_scaffold.dart';

void main() {
  runApp(
    const ProviderScope(
      child: CarrotApp(),
    ),
  );
}

class CarrotApp extends ConsumerWidget {
  const CarrotApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // SharedPreferences에서 토큰 복원 완료 전까지 스플래시 표시
    // 복원 완료(data) 또는 오류(error) 모두 MainScaffold로 진행
    final tokenInit = ref.watch(tokenInitializerProvider);

    return MaterialApp(
      title: 'carrot',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: tokenInit.when(
        data: (_) {
          final token = ref.watch(tokenProvider);
          return token != null ? const MainScaffold() : const LoginScreen();
        },
        loading: () => const _SplashScreen(),
        error: (err, st) => const LoginScreen(), // 복원 실패 시 로그인 화면으로
      ),
    );
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
