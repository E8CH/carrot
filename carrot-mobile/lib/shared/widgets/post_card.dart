import 'package:flutter/material.dart';
import 'shimmer_box.dart';
import 'status_badge.dart';

class PostCard extends StatelessWidget {
  final Map<String, dynamic> post;
  final VoidCallback? onTap;

  const PostCard({super.key, required this.post, this.onTap});

  String _timeAgo(String isoDate) {
    final date = DateTime.tryParse(isoDate);
    if (date == null) return '';
    final diff = DateTime.now().toUtc().difference(date.toUtc());
    if (diff.inMinutes < 1) return '방금 전';
    if (diff.inMinutes < 60) return '${diff.inMinutes}분 전';
    if (diff.inHours < 24) return '${diff.inHours}시간 전';
    return '${diff.inDays}일 전';
  }

  @override
  Widget build(BuildContext context) {
    final title = post['title'] as String? ?? '';
    final price = post['price'] as int?;
    final isFree = post['is_free'] as bool? ?? false;
    final status = post['status'] as String? ?? '판매중';
    final thumbnail = post['thumbnail'] as String?;
    final chatCount = post['chat_count'] as int? ?? 0;
    final likeCount = post['like_count'] as int? ?? 0;
    final createdAt = post['created_at'] as String? ?? '';

    final priceText = isFree
        ? '나눔'
        : price != null
            ? '${price.toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (m) => '${m.group(1)},')}원'
            : '가격 미정';

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: thumbnail != null
                      ? Image.network(
                          thumbnail,
                          width: 100,
                          height: 100,
                          fit: BoxFit.cover,
                          loadingBuilder: (ctx, child, progress) {
                            if (progress == null) return child;
                            return const ShimmerBox(
                                width: 100, height: 100, borderRadius: 0);
                          },
                          errorBuilder: (ctx, err, st) => _placeholder(),
                        )
                      : _placeholder(),
                ),
                Positioned(
                  top: 4,
                  left: 4,
                  child: StatusBadge(status: status),
                ),
              ],
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontSize: 15, fontWeight: FontWeight.w500)),
                  const SizedBox(height: 4),
                  Text(priceText,
                      style: const TextStyle(
                          fontSize: 14, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Text(
                    '채팅 $chatCount  관심 $likeCount  ${_timeAgo(createdAt)}',
                    style:
                        const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _placeholder() => Container(
        width: 100,
        height: 100,
        color: const Color(0xFFE5E7EB),
        child:
            const Icon(Icons.image_outlined, color: Colors.white54, size: 36),
      );
}

class PostCardSkeleton extends StatelessWidget {
  const PostCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const ShimmerBox(width: 100, height: 100, borderRadius: 12),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const ShimmerBox(height: 16),
                const SizedBox(height: 6),
                ShimmerBox(width: 120, height: 14),
                const SizedBox(height: 10),
                ShimmerBox(width: 160, height: 12),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
