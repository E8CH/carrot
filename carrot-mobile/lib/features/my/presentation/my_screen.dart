import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/api_client_provider.dart';
import '../../../core/providers/token_provider.dart';
import '../../../features/auth/presentation/login_screen.dart';
import '../../../features/posts/data/posts_repository.dart';
import '../../../features/posts/presentation/post_detail_screen.dart';
import '../../../shared/widgets/manner_temp_widget.dart';
import '../../../shared/widgets/post_card.dart';
import '../data/my_repository.dart';

final myProfileProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.read(apiClientProvider);
  final repo = MyRepository(client);
  return await repo.getMe();
});

final myPostsProvider = FutureProvider.autoDispose
    .family<Map<String, dynamic>, String?>((ref, status) async {
  final client = ref.read(apiClientProvider);
  final repo = MyRepository(client);
  return await repo.getMyPosts(status: status);
});

final myPurchasesProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.read(apiClientProvider);
  final repo = MyRepository(client);
  return await repo.getMyPurchases();
});

final myLikesProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.read(apiClientProvider);
  final repo = MyRepository(client);
  return await repo.getMyLikes();
});

class MyScreen extends ConsumerStatefulWidget {
  const MyScreen({super.key});

  @override
  ConsumerState<MyScreen> createState() => _MyScreenState();
}

class _MyScreenState extends ConsumerState<MyScreen> {
  String? _selectedStatus;

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(myProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('나의 당근')),
      body: profile.when(
        data: (data) => _ProfileContent(
          data: data,
          selectedStatus: _selectedStatus,
          onStatusFilterChanged: (s) => setState(() => _selectedStatus = s),
          onLogout: () => _logout(context),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('프로필을 불러올 수 없습니다.', style: TextStyle(color: Colors.red)),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () => ref.refresh(myProfileProvider),
                child: const Text('다시 시도'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _logout(BuildContext context) async {
    await clearToken(ref);
    if (context.mounted) {
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
        (route) => false,
      );
    }
  }
}

class _ProfileContent extends ConsumerStatefulWidget {
  final Map<String, dynamic> data;
  final String? selectedStatus;
  final ValueChanged<String?> onStatusFilterChanged;
  final VoidCallback onLogout;

  const _ProfileContent({
    required this.data,
    required this.selectedStatus,
    required this.onStatusFilterChanged,
    required this.onLogout,
  });

  @override
  ConsumerState<_ProfileContent> createState() => _ProfileContentState();
}

class _ProfileContentState extends ConsumerState<_ProfileContent> {
  int? _changingId;

  static const _filters = [
    (label: '전체', value: null),
    (label: '판매중', value: '판매중'),
    (label: '예약중', value: '예약중'),
    (label: '거래완료', value: '거래완료'),
  ];

  Widget _thumbPlaceholder() => Container(
        width: 60,
        height: 60,
        color: const Color(0xFFE5E7EB),
        child: const Icon(Icons.image_outlined, color: Colors.white54, size: 28),
      );

  String _formatDate(String? isoString) {
    if (isoString == null) return '';
    final date = DateTime.tryParse(isoString)?.toLocal();
    if (date == null) return '';
    return '${date.year}.${date.month.toString().padLeft(2, '0')}.${date.day.toString().padLeft(2, '0')}';
  }

  Future<void> _changeStatus(int postId, String newStatus) async {
    setState(() => _changingId = postId);
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      await repo.changeStatus(postId, newStatus);
      ref.invalidate(myPostsProvider(widget.selectedStatus));
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('상태 변경에 실패했습니다.')),
        );
      }
    } finally {
      if (mounted) setState(() => _changingId = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    final rawTemp = widget.data['manner_temp'];
    final mannerTemp = rawTemp is num
        ? rawTemp.toDouble()
        : double.tryParse(rawTemp?.toString() ?? '') ?? 36.5;

    final myPosts = ref.watch(myPostsProvider(widget.selectedStatus));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 프로필
          Center(child: MannerTempWidget(temp: mannerTemp)),
          const SizedBox(height: 24),
          _InfoRow(label: '이메일', value: widget.data['email'] as String? ?? ''),
          _InfoRow(label: '주소', value: widget.data['address'] as String? ?? ''),
          _InfoRow(label: '연락처', value: widget.data['phone'] as String? ?? ''),
          const SizedBox(height: 32),

          // 판매관리 섹션
          const Text('판매관리', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),

          // 상태 필터 탭
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _filters.map((f) {
                final active = widget.selectedStatus == f.value;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: GestureDetector(
                    onTap: () => widget.onStatusFilterChanged(f.value),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                      decoration: BoxDecoration(
                        color: active ? const Color(0xFFFFF3EE) : Colors.white,
                        border: Border.all(
                          color: active ? const Color(0xFFFF7E36) : Colors.grey.shade300,
                        ),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        f.label,
                        style: TextStyle(
                          fontSize: 13,
                          color: active ? const Color(0xFFFF7E36) : Colors.grey.shade600,
                          fontWeight: active ? FontWeight.w600 : FontWeight.normal,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 12),

          // 게시글 목록
          myPosts.when(
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 32),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (e, _) => const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Center(child: Text('게시글을 불러올 수 없습니다.', style: TextStyle(color: Colors.red))),
            ),
            data: (data) {
              final items = (data['items'] as List?) ?? [];
              if (items.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.symmetric(vertical: 32),
                  child: Center(
                    child: Text('등록한 게시글이 없어요.', style: TextStyle(color: Colors.grey)),
                  ),
                );
              }
              return Column(
                children: items.map((item) {
                  final post = item as Map<String, dynamic>;
                  final postId = post['id'] as int;
                  final status = post['status'] as String? ?? '';
                  return Container(
                    margin: const EdgeInsets.only(bottom: 4),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.grey.shade100),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        PostCard(
                          post: post,
                          onTap: () => Navigator.of(context).push(MaterialPageRoute(
                            builder: (_) => PostDetailScreen(postId: postId),
                          )).then((_) => ref.invalidate(myPostsProvider(widget.selectedStatus))),
                        ),
                        if (status != '거래완료')
                          Padding(
                            padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                            child: Row(
                              children: [
                                if (status == '판매중')
                                  _StatusButton(
                                    label: _changingId == postId ? '변경 중...' : '예약중으로 변경',
                                    enabled: _changingId != postId,
                                    onTap: () => _changeStatus(postId, '예약중'),
                                  ),
                                if (status == '예약중')
                                  _StatusButton(
                                    label: _changingId == postId ? '변경 중...' : '판매중으로 변경',
                                    enabled: _changingId != postId,
                                    onTap: () => _changeStatus(postId, '판매중'),
                                  ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  );
                }).toList(),
              );
            },
          ),

          const SizedBox(height: 32),

          // 구매내역 섹션
          const Text('구매내역', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ref.watch(myPurchasesProvider).when(
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (e, _) => const Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: Center(child: Text('구매내역을 불러올 수 없습니다.', style: TextStyle(color: Colors.red))),
            ),
            data: (data) {
              final items = (data['items'] as List?) ?? [];
              if (items.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Center(
                    child: Text('구매내역이 없어요.', style: TextStyle(color: Colors.grey)),
                  ),
                );
              }
              return Column(
                children: items.map((item) {
                  final m = item as Map<String, dynamic>;
                  final postId = m['id'] as int;
                  final title = m['title'] as String? ?? '';
                  final price = m['price'] as int?;
                  final isFree = m['is_free'] as bool? ?? false;
                  final thumbnail = m['thumbnail'] as String?;
                  final updatedAt = m['updated_at'] as String?;

                  final priceText = isFree
                      ? '나눔'
                      : price != null
                          ? '${price.toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (m) => '${m.group(1)},')}원'
                          : '가격 미정';

                  final dateText = _formatDate(updatedAt);

                  return InkWell(
                    onTap: () => Navigator.of(context).push(MaterialPageRoute(
                      builder: (_) => PostDetailScreen(postId: postId),
                    )),
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 4),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.grey.shade100),
                      ),
                      child: Row(
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: thumbnail != null
                                ? Image.network(thumbnail, width: 60, height: 60, fit: BoxFit.cover,
                                    errorBuilder: (ctx, e, s) => _thumbPlaceholder())
                                : _thumbPlaceholder(),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(title, maxLines: 1, overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                                const SizedBox(height: 2),
                                Text(priceText, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                                if (dateText.isNotEmpty) ...[
                                  const SizedBox(height: 2),
                                  Text('거래완료 $dateText', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                                ],
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              );
            },
          ),

          const SizedBox(height: 32),

          // 관심목록 섹션
          const Text('관심목록', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ref.watch(myLikesProvider).when(
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (e, _) => const Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: Center(child: Text('관심목록을 불러올 수 없습니다.', style: TextStyle(color: Colors.red))),
            ),
            data: (data) {
              final items = (data['items'] as List?) ?? [];
              if (items.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Center(
                    child: Text('관심목록이 없어요.', style: TextStyle(color: Colors.grey)),
                  ),
                );
              }
              return Column(
                children: items.map((item) {
                  final post = item as Map<String, dynamic>;
                  final postId = post['id'] as int;
                  return PostCard(
                    post: post,
                    onTap: () => Navigator.of(context).push(MaterialPageRoute(
                      builder: (_) => PostDetailScreen(postId: postId),
                    )),
                  );
                }).toList(),
              );
            },
          ),

          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: widget.onLogout,
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.red,
                side: const BorderSide(color: Colors.red),
              ),
              child: const Text('로그아웃'),
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusButton extends StatelessWidget {
  final String label;
  final bool enabled;
  final VoidCallback onTap;

  const _StatusButton({required this.label, required this.enabled, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: enabled ? onTap : null,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
        decoration: BoxDecoration(
          border: Border.all(color: enabled ? Colors.grey.shade400 : Colors.grey.shade200),
          borderRadius: BorderRadius.circular(16),
          color: enabled ? Colors.white : Colors.grey.shade50,
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: enabled ? Colors.grey.shade700 : Colors.grey.shade400,
          ),
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 2),
          Text(value, style: const TextStyle(fontSize: 16)),
          const Divider(),
        ],
      ),
    );
  }
}
