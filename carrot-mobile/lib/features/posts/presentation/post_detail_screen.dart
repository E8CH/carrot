import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_endpoints.dart';
import '../../../core/providers/api_client_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/manner_temp_widget.dart';
import '../../../shared/widgets/shimmer_box.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../chats/data/chats_repository.dart';
import '../../chats/presentation/chat_room_screen.dart';
import '../data/posts_repository.dart';
import '../../../shared/widgets/trade_complete_sheet.dart';
import '../../reviews/presentation/review_form_screen.dart';
import 'post_edit_screen.dart';

class PostDetailScreen extends ConsumerStatefulWidget {
  final int postId;
  const PostDetailScreen({super.key, required this.postId});

  @override
  ConsumerState<PostDetailScreen> createState() => _PostDetailScreenState();
}

class _PostDetailScreenState extends ConsumerState<PostDetailScreen> {
  Map<String, dynamic>? _post;
  bool _loading = true;
  String? _error;
  bool _isOwner = false;
  bool _isLoggedIn = false;
  bool _isLiked = false;
  int _likeCount = 0;
  bool _chatLoading = false;
  bool _statusLoading = false;
  String? _myEmail;
  int _imageIdx = 0;
  final _pageCtrl = PageController();

  @override
  void initState() {
    super.initState();
    _loadPost();
  }

  @override
  void dispose() {
    _pageCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadPost() async {
    try {
      debugPrint('[DETAIL] _loadPost start id=${widget.postId}');
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      final post = await repo.getPost(widget.postId);
      debugPrint('[DETAIL] _loadPost success title=${post['title']}');
      if (!mounted) return;
      setState(() {
        _post = post;
        _isLiked = post['is_liked'] as bool? ?? false;
        _likeCount = post['like_count'] as int? ?? 0;
        _loading = false;
      });
      _checkOwner(post['seller_email'] as String? ?? '');
    } catch (e) {
      debugPrint('[DETAIL] _loadPost error: $e');
      if (!mounted) return;
      setState(() {
        _error = '게시글을 불러올 수 없습니다.';
        _loading = false;
      });
    }
  }

  Future<void> _confirmDelete(BuildContext ctx) async {
    final nav = Navigator.of(ctx);
    final messenger = ScaffoldMessenger.of(ctx);
    final confirm = await showDialog<bool>(
      context: ctx,
      builder: (dlgCtx) => AlertDialog(
        title: const Text('게시글을 삭제할까요?'),
        content: const Text('삭제하면 복구할 수 없습니다.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dlgCtx, false), child: const Text('취소')),
          TextButton(
            onPressed: () => Navigator.pop(dlgCtx, true),
            child: const Text('삭제', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
    if (confirm != true || !mounted) return;
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      await repo.deletePost(widget.postId);
      nav.pop();
    } catch (_) {
      messenger.showSnackBar(const SnackBar(content: Text('삭제에 실패했습니다.')));
    }
  }

  Future<void> _checkOwner(String sellerEmail) async {
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.get(ApiEndpoints.usersMe);
      final myEmail = (res as Map<String, dynamic>)['email'] as String?;
      if (mounted) setState(() {
        _isOwner = myEmail == sellerEmail;
        _isLoggedIn = true;
        _myEmail = myEmail;
      });
    } catch (_) {
      // 비로그인 시 isOwner = false, isLoggedIn = false 유지
    }
  }

  Future<void> _toggleLike() async {
    if (!_isLoggedIn) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('찜하기는 로그인 후 이용할 수 있습니다.')),
        );
      }
      return;
    }
    final prevLiked = _isLiked;
    final prevCount = _likeCount;
    if (mounted) setState(() {
      _isLiked = !_isLiked;
      _likeCount = _isLiked ? _likeCount + 1 : _likeCount - 1;
    });
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      final result = await repo.toggleLike(widget.postId);
      if (mounted) setState(() {
        _isLiked = result['is_liked'] as bool? ?? prevLiked;
        _likeCount = result['like_count'] as int? ?? prevCount;
      });
    } catch (_) {
      if (mounted) setState(() { _isLiked = prevLiked; _likeCount = prevCount; });
    }
  }

  void _showTradeCompleteSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => TradeCompleteSheet(
        postId: widget.postId,
        onComplete: (String? targetEmail) {
          _loadPost();
          if (targetEmail != null && mounted) {
            Navigator.of(context).push(MaterialPageRoute(
              builder: (_) => ReviewFormScreen(
                postId: widget.postId,
                targetEmail: targetEmail,
              ),
            )).then((_) { if (mounted) _loadPost(); });
          }
        },
      ),
    );
  }

  Future<void> _changeStatus(String newStatus) async {
    if (_statusLoading) return;
    final messenger = ScaffoldMessenger.of(context);
    if (mounted) setState(() => _statusLoading = true);
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      await repo.changeStatus(widget.postId, newStatus);
      await _loadPost();
    } catch (_) {
      messenger.showSnackBar(const SnackBar(content: Text('상태 변경에 실패했습니다.')));
    } finally {
      if (mounted) setState(() => _statusLoading = false);
    }
  }

  Future<void> _handleChat() async {
    if (_chatLoading) return;
    final messenger = ScaffoldMessenger.of(context);
    if (mounted) setState(() => _chatLoading = true);
    try {
      final client = ref.read(apiClientProvider);
      final repo = ChatsRepository(client);
      final result = await repo.createOrGetRoom(widget.postId);
      final roomId = result['room_id'] as String;
      final sellerEmail = result['seller_email'] as String;
      if (mounted) {
        final buyerEmail = result['buyer_email'] as String? ?? '';
        Navigator.of(context).push(MaterialPageRoute(
          builder: (_) => ChatRoomScreen(
            roomId: roomId,
            sellerEmail: sellerEmail,
            buyerEmail: buyerEmail,
            myEmail: _myEmail ?? buyerEmail,
            postId: widget.postId,
          ),
        ));
      }
    } catch (_) {
      messenger.showSnackBar(const SnackBar(content: Text('채팅방 생성에 실패했습니다.')));
    } finally {
      if (mounted) setState(() => _chatLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        body: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const ShimmerBox(height: 240, borderRadius: 0),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      const ShimmerBox(width: 40, height: 40, borderRadius: 20),
                      const SizedBox(width: 12),
                      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        ShimmerBox(width: 140, height: 14),
                        const SizedBox(height: 6),
                        ShimmerBox(width: 80, height: 12),
                      ]),
                    ]),
                    const SizedBox(height: 20),
                    const ShimmerBox(height: 22),
                    const SizedBox(height: 10),
                    ShimmerBox(width: 100, height: 20),
                    const SizedBox(height: 20),
                    const ShimmerBox(height: 14),
                    const SizedBox(height: 8),
                    const ShimmerBox(height: 14),
                    const SizedBox(height: 8),
                    ShimmerBox(width: 200, height: 14),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
    }
    if (_error != null || _post == null) {
      return Scaffold(
        appBar: AppBar(),
        body: Center(child: Text(_error ?? '알 수 없는 오류', style: const TextStyle(color: Colors.red))),
      );
    }

    final post = _post!;
    final photos = (post['photos'] as List?)?.cast<String>() ?? [];
    final title = post['title'] as String? ?? '';
    final description = post['description'] as String? ?? '';
    final price = post['price'] as int?;
    final isFree = post['is_free'] as bool? ?? false;
    final status = post['status'] as String? ?? '판매중';
    final tradePlace = post['trade_place'] as String?;
    final viewCount = post['view_count'] as int? ?? 0;
    final chatCount = post['chat_count'] as int? ?? 0;
    final likeCount = post['like_count'] as int? ?? 0;
    final sellerEmail = post['seller_email'] as String? ?? '';
    final mannerTemp = (post['manner_temp'] as num?)?.toDouble() ?? 36.5;

    final priceText = isFree
        ? '나눔'
        : price != null
            ? '${price.toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (m) => '${m.group(1)},')}원'
            : '가격 미정';

    return Scaffold(
      body: Column(
        children: [
          // 스크롤 가능 영역
          Expanded(
            child: CustomScrollView(
              slivers: [
                // AppBar (이미지 슬라이더 위)
                SliverAppBar(
                  expandedHeight: 240,
                  pinned: true,
                  leading: IconButton(
                    icon: const Icon(Icons.arrow_back),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                  flexibleSpace: FlexibleSpaceBar(
                    background: _buildImageSlider(photos),
                  ),
                ),

                SliverToBoxAdapter(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 판매자 프로필
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            CircleAvatar(
                              radius: 20,
                              backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                              child: const Text('👤'),
                            ),
                            const SizedBox(width: 12),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(sellerEmail, style: const TextStyle(fontWeight: FontWeight.w600)),
                                MannerTempWidget(temp: mannerTemp),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const Divider(height: 1),

                      // 본문
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(title,
                                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                                ),
                                StatusBadge(status: status),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(priceText,
                                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
                            const SizedBox(height: 16),
                            Text(description,
                                style: const TextStyle(fontSize: 14, height: 1.6, color: Colors.black87)),
                            if (tradePlace != null) ...[
                              const SizedBox(height: 12),
                              Row(children: [
                                const Icon(Icons.location_on_outlined, size: 14, color: Colors.grey),
                                const SizedBox(width: 4),
                                Text(tradePlace,
                                    style: const TextStyle(fontSize: 13, color: Colors.grey)),
                              ]),
                            ],
                            const SizedBox(height: 16),
                            const Divider(height: 1),
                            const SizedBox(height: 12),
                            Text(
                              '채팅 $chatCount  관심 $likeCount  조회 $viewCount',
                              style: const TextStyle(fontSize: 12, color: Colors.grey),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // 하단 고정 버튼
          SafeArea(
            top: false,
            child: Container(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(top: BorderSide(color: Colors.grey.shade200)),
            ),
            child: _isOwner
                ? Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (status != '거래완료') ...[
                        Row(children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: _showTradeCompleteSheet,
                              style: OutlinedButton.styleFrom(
                                foregroundColor: const Color(0xFFFF7E36),
                                side: const BorderSide(color: Color(0xFFFF7E36)),
                              ),
                              child: const Text('거래완료'),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: OutlinedButton(
                              onPressed: _statusLoading
                                  ? null
                                  : () => _changeStatus(status == '판매중' ? '예약중' : '판매중'),
                              child: Text(status == '판매중' ? '예약중으로' : '판매중으로'),
                            ),
                          ),
                        ]),
                        const SizedBox(height: 8),
                      ],
                      Row(children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => PostEditScreen(postId: widget.postId),
                              ),
                            ).then((_) => _loadPost()),
                            child: const Text('수정'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => _confirmDelete(context),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.red,
                              side: const BorderSide(color: Colors.red),
                            ),
                            child: const Text('삭제'),
                          ),
                        ),
                      ]),
                    ],
                  )
                : Row(children: [
                    OutlinedButton(
                      onPressed: _toggleLike,
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(56, 48),
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(_isLiked ? '❤️' : '🤍', style: const TextStyle(fontSize: 18)),
                          Text('$_likeCount', style: const TextStyle(fontSize: 10)),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: SizedBox(
                        height: 48,
                        child: ElevatedButton(
                          onPressed: _chatLoading ? null : _handleChat,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          child: Text(
                            _chatLoading ? '연결 중...' : '채팅하기',
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ),
                  ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImageSlider(List<String> photos) {
    if (photos.isEmpty) {
      return Container(
        color: Colors.grey.shade100,
        child: const Icon(Icons.image_outlined, size: 64, color: Colors.grey),
      );
    }

    return Stack(
      children: [
        PageView.builder(
          controller: _pageCtrl,
          onPageChanged: (i) => setState(() => _imageIdx = i),
          itemCount: photos.length,
          itemBuilder: (ctx, i) => Image.network(
            photos[i],
            fit: BoxFit.cover,
            loadingBuilder: (ctx, child, loadingProgress) {
              if (loadingProgress == null) return child;
              return Container(
                color: Colors.grey.shade200,
                child: Center(
                  child: CircularProgressIndicator(
                    value: loadingProgress.expectedTotalBytes != null
                        ? loadingProgress.cumulativeBytesLoaded /
                            loadingProgress.expectedTotalBytes!
                        : null,
                    strokeWidth: 2,
                    valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFF7E36)),
                  ),
                ),
              );
            },
            errorBuilder: (ctx, err, st) => Container(
              color: Colors.grey.shade100,
              child: const Icon(Icons.broken_image_outlined, color: Colors.grey),
            ),
          ),
        ),
        if (photos.length > 1)
          Positioned(
            bottom: 8,
            left: 0,
            right: 0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(
                photos.length,
                (i) => AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.symmetric(horizontal: 2),
                  width: i == _imageIdx ? 8 : 6,
                  height: 6,
                  decoration: BoxDecoration(
                    color: i == _imageIdx ? Colors.white : Colors.white54,
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
