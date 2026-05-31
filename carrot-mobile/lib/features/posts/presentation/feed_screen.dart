import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/api_client_provider.dart';
import '../../../shared/widgets/post_card.dart';
import '../../../shared/widgets/shimmer_box.dart';
import '../data/posts_repository.dart';
import 'post_detail_screen.dart';

class FeedScreen extends ConsumerStatefulWidget {
  const FeedScreen({super.key});

  @override
  ConsumerState<FeedScreen> createState() => _FeedScreenState();
}

class _FeedScreenState extends ConsumerState<FeedScreen> {
  final _scrollController = ScrollController();
  final List<Map<String, dynamic>> _posts = [];
  int _page = 1;
  bool _loading = false;
  bool _hasMore = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    _loadPosts();
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
            _scrollController.position.maxScrollExtent - 200 &&
        !_loading &&
        _hasMore) {
      _loadPosts();
    }
  }

  Future<void> _loadPosts() async {
    if (_loading || !_hasMore) return;
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      final data = await repo.getPosts(page: _page);
      final rawItems = data['items'];
      if (rawItems is! List) throw const FormatException('items 필드가 올바르지 않습니다.');
      final items = rawItems.whereType<Map<String, dynamic>>().toList();
      final pageSize = (data['size'] as num?)?.toInt() ?? 20;

      setState(() {
        _posts.addAll(items);
        _page++;
        _hasMore = items.length >= pageSize;
      });
    } catch (e) {
      setState(() => _error = '게시글을 불러올 수 없습니다.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Widget _buildSkeletonList() {
    return ListView.separated(
      itemCount: 6,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (_, __) => const PostCardSkeleton(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🥕 carrot', style: TextStyle(color: Color(0xFFFF7E36))),
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          setState(() {
            _posts.clear();
            _page = 1;
            _hasMore = true;
          });
          await _loadPosts();
        },
        child: _posts.isEmpty && _loading
            ? _buildSkeletonList()
            : _posts.isEmpty
                ? _error != null
                    ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
                    : const Center(child: Text('게시글이 없습니다.', style: TextStyle(color: Colors.grey)))
                : ListView.separated(
                controller: _scrollController,
                itemCount: _posts.length + (_hasMore ? 1 : 0),
                separatorBuilder: (ctx, idx) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  if (index == _posts.length) {
                    return _loading
                        ? const Padding(
                            padding: EdgeInsets.all(16),
                            child: Center(child: CircularProgressIndicator()),
                          )
                        : const SizedBox.shrink();
                  }
                  final postId = _posts[index]['id'] as int? ?? 0;
                  return PostCard(
                    post: _posts[index],
                    onTap: postId > 0
                        ? () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => PostDetailScreen(postId: postId),
                              ),
                            )
                        : null,
                  );
                },
              ),
      ),
    );
  }
}
