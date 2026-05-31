import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/providers/api_client_provider.dart';
import '../../../core/providers/token_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/main_scaffold.dart';
import '../data/auth_repository.dart';
import 'register_screen.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();

  bool _loading = false;
  String _error = '';

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = '';
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final repo = AuthRepository(apiClient);
      final data = await repo.login(
        email: _emailCtrl.text.trim(),
        password: _passwordCtrl.text,
      );

      final token = data['access_token'];
      if (token == null || token is! String) {
        throw const FormatException('서버 응답에 access_token이 없습니다.');
      }
      await saveToken(ref, token);

      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const MainScaffold()),
          (route) => false,
        );
      }
    } on ApiException catch (e) {
      setState(() => _error = e.detail);
    } on FormatException catch (e) {
      setState(() => _error = e.message.isNotEmpty ? e.message : '서버 응답을 처리할 수 없습니다.');
    } catch (_) {
      setState(() => _error = '로그인에 실패했습니다.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('로그인')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 16),
              Text(
                '🥕 carrot',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                '이메일과 비밀번호로 로그인하세요',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 32),

              TextFormField(
                controller: _emailCtrl,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: '이메일',
                  hintText: 'example@email.com',
                  border: OutlineInputBorder(),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return '이메일을 입력하세요.';
                  if (!v.contains('@')) return '유효한 이메일을 입력하세요.';
                  return null;
                },
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _passwordCtrl,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: '비밀번호',
                  hintText: '비밀번호 입력',
                  border: OutlineInputBorder(),
                ),
                validator: (v) => (v == null || v.isEmpty) ? '비밀번호를 입력하세요.' : null,
              ),
              const SizedBox(height: 8),

              if (_error.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 4, bottom: 4),
                  child: Text(
                    _error,
                    style: const TextStyle(color: Colors.red, fontSize: 13),
                  ),
                ),

              const SizedBox(height: 16),
              FilledButton(
                onPressed: _loading ? null : _submit,
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  minimumSize: const Size.fromHeight(48),
                ),
                child: _loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Text('로그인', style: TextStyle(fontSize: 16)),
              ),
              const SizedBox(height: 16),

              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('아직 계정이 없으신가요?', style: TextStyle(color: Colors.grey)),
                  TextButton(
                    onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const RegisterScreen()),
                    ),
                    child: Text('회원가입', style: TextStyle(color: AppColors.primary)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
