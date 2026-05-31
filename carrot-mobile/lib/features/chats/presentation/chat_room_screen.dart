import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/api_client_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../features/posts/data/posts_repository.dart';
import '../../../shared/widgets/status_badge.dart';
import '../data/chats_repository.dart';

class _OptimisticMessage {
  final int tempId;
  final String message;
  bool pending;
  bool error;
  _OptimisticMessage({
    required this.tempId,
    required this.message,
    this.pending = true,
    this.error = false,
  });
}

class ChatRoomScreen extends ConsumerStatefulWidget {
  final String roomId;
  final String sellerEmail;
  final String buyerEmail;
  final String myEmail;
  final int postId;

  const ChatRoomScreen({
    super.key,
    required this.roomId,
    required this.sellerEmail,
    required this.buyerEmail,
    required this.myEmail,
    required this.postId,
  });

  @override
  ConsumerState<ChatRoomScreen> createState() => _ChatRoomScreenState();
}

class _ChatRoomScreenState extends ConsumerState<ChatRoomScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  List<Map<String, dynamic>> _messages = [];
  final List<_OptimisticMessage> _optimisticMessages = [];
  int? _lastMessageId;
  bool _sending = false;
  Timer? _pollTimer;
  Map<String, dynamic>? _post;

  String get _opponentEmail =>
      widget.myEmail == widget.sellerEmail ? widget.buyerEmail : widget.sellerEmail;

  @override
  void initState() {
    super.initState();
    _loadPost();
    _loadMessages();
    _markAsRead();
    _pollTimer = Timer.periodic(
      const Duration(milliseconds: 2500),
      (_) => _pollNewMessages(),
    );
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadPost() async {
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      final post = await repo.getPost(widget.postId);
      if (mounted) setState(() => _post = post);
    } catch (_) {}
  }

  Future<void> _markAsRead() async {
    try {
      final client = ref.read(apiClientProvider);
      final repo = ChatsRepository(client);
      await repo.markAsRead(widget.roomId);
    } catch (_) {}
  }

  Future<void> _loadMessages() async {
    try {
      final client = ref.read(apiClientProvider);
      final repo = ChatsRepository(client);
      final result = await repo.getMessages(widget.roomId);
      if (!mounted) return;
      setState(() {
        _messages = result;
        if (result.isNotEmpty) {
          _lastMessageId = result.last['id'] as int?;
        }
      });
      _scrollToBottom();
    } catch (_) {}
  }

  Future<void> _pollNewMessages() async {
    if (!mounted) return;
    try {
      final client = ref.read(apiClientProvider);
      final repo = ChatsRepository(client);
      final newMsgs = await repo.getMessages(widget.roomId, afterId: _lastMessageId);
      if (newMsgs.isNotEmpty && mounted) {
        setState(() {
          _messages.addAll(newMsgs);
          _lastMessageId = newMsgs.last['id'] as int?;
          // 확인된 낙관적 메시지 제거
          _optimisticMessages.removeWhere(
            (om) => newMsgs.any(
              (m) => m['message'] == om.message && m['sender_email'] == widget.myEmail,
            ),
          );
        });
        _scrollToBottom();
      }
    } catch (_) {}
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _sending) return;
    _controller.clear();
    final tempId = DateTime.now().millisecondsSinceEpoch;
    setState(() {
      _sending = true;
      _optimisticMessages.add(_OptimisticMessage(tempId: tempId, message: text));
    });
    _scrollToBottom();
    try {
      final client = ref.read(apiClientProvider);
      final repo = ChatsRepository(client);
      await repo.sendMessage(widget.roomId, text, widget.postId);
    } catch (_) {
      if (mounted) {
        setState(() {
          final idx = _optimisticMessages.indexWhere((m) => m.tempId == tempId);
          if (idx != -1) {
            _optimisticMessages[idx].pending = false;
            _optimisticMessages[idx].error = true;
          }
        });
      }
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Widget _buildPostBanner(Map<String, dynamic> post) {
    final photos = (post['photos'] as List?)?.cast<String>() ?? [];
    final thumbnail = post['thumbnail'] as String? ?? (photos.isNotEmpty ? photos[0] : null);
    final title = post['title'] as String? ?? '';
    final price = post['price'] as int?;
    final isFree = post['is_free'] as bool? ?? false;
    final status = post['status'] as String? ?? '판매중';
    final priceText = isFree
        ? '나눔'
        : price != null
            ? '${price.toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (m) => '${m.group(1)},')}원'
            : '가격 미정';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: Colors.grey.shade200)),
      ),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: thumbnail != null
                ? Image.network(
                    thumbnail,
                    width: 48,
                    height: 48,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => _thumbPlaceholder(),
                  )
                : _thumbPlaceholder(),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 2),
                Text(
                  priceText,
                  style: const TextStyle(fontSize: 13, color: Colors.black87),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          StatusBadge(status: status),
        ],
      ),
    );
  }

  Widget _thumbPlaceholder() => Container(
        width: 48,
        height: 48,
        color: const Color(0xFFE5E7EB),
        child: const Icon(Icons.image_outlined, color: Colors.white54, size: 22),
      );

  Widget _buildBubble(
    String message,
    bool isMine, {
    bool pending = false,
    bool error = false,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 3),
      child: Align(
        alignment: isMine ? Alignment.centerRight : Alignment.centerLeft,
        child: Container(
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.72,
          ),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: isMine ? AppColors.primary : const Color(0xFFF3F4F6),
            borderRadius: BorderRadius.only(
              topLeft: const Radius.circular(18),
              topRight: const Radius.circular(18),
              bottomLeft: Radius.circular(isMine ? 18 : 4),
              bottomRight: Radius.circular(isMine ? 4 : 18),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Flexible(
                child: Text(
                  message,
                  style: TextStyle(
                    color: isMine ? Colors.white : Colors.black87,
                    fontSize: 14,
                  ),
                ),
              ),
              if (pending) ...[
                const SizedBox(width: 4),
                const SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(strokeWidth: 1.5, color: Colors.white70),
                ),
              ],
              if (error) ...[
                const SizedBox(width: 4),
                const Icon(Icons.error_outline, size: 14, color: Colors.red),
              ],
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          _opponentEmail,
          style: const TextStyle(fontSize: 15),
          overflow: TextOverflow.ellipsis,
        ),
      ),
      body: Column(
        children: [
          if (_post != null) _buildPostBanner(_post!),
          Expanded(
            child: ListView(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(vertical: 8),
              children: [
                for (final msg in _messages)
                  _buildBubble(
                    msg['message'] as String? ?? '',
                    (msg['sender_email'] as String?) == widget.myEmail,
                  ),
                for (final om in _optimisticMessages)
                  _buildBubble(om.message, true, pending: om.pending, error: om.error),
              ],
            ),
          ),
          Container(
            padding: EdgeInsets.fromLTRB(
              12,
              8,
              12,
              MediaQuery.of(context).padding.bottom + 8,
            ),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(top: BorderSide(color: Colors.grey.shade200)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: '메시지 입력...',
                      filled: true,
                      fillColor: Colors.grey.shade100,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 10,
                      ),
                    ),
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                    maxLines: null,
                  ),
                ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: _sending ? null : _sendMessage,
                  child: Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: _sending
                          ? AppColors.primary.withValues(alpha: 0.4)
                          : AppColors.primary,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.send, color: Colors.white, size: 20),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
