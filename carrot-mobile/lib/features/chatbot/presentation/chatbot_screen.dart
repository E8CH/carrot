import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/api_client_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../data/chatbot_repository.dart';

class _Message {
  final bool isUser;
  final String content;
  const _Message({required this.isUser, required this.content});
}

class ChatBotScreen extends ConsumerStatefulWidget {
  const ChatBotScreen({super.key});

  @override
  ConsumerState<ChatBotScreen> createState() => _ChatBotScreenState();
}

class _ChatBotScreenState extends ConsumerState<ChatBotScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<_Message> _messages = [
    const _Message(
      isUser: false,
      content: '안녕하세요! carrot 도움말 챗봇입니다.\n궁금한 점을 물어보세요 😊',
    ),
  ];
  bool _loading = false;

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;
    _controller.clear();
    setState(() {
      _messages.add(_Message(isUser: true, content: text));
      _loading = true;
    });
    _scrollToBottom();
    try {
      final repo = ChatbotRepository(ref.read(apiClientProvider));
      final answer = await repo.chat(text);
      if (mounted) {
        setState(() => _messages.add(_Message(isUser: false, content: answer)));
        _scrollToBottom();
      }
    } catch (_) {
      if (mounted) {
        setState(() => _messages.add(const _Message(
          isUser: false,
          content: '죄송합니다. 잠시 후 다시 시도해주세요.',
        )));
        _scrollToBottom();
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Text('🥕', style: TextStyle(fontSize: 18)),
            SizedBox(width: 8),
            Text('carrot 도움말', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
          ],
        ),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              itemCount: _messages.length + (_loading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length) return const _TypingIndicator();
                final msg = _messages[index];
                return _MessageBubble(message: msg);
              },
            ),
          ),
          _InputBar(controller: _controller, loading: _loading, onSend: _send),
        ],
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final _Message message;
  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 14,
              backgroundColor: AppColors.primary,
              child: const Text('🥕', style: TextStyle(fontSize: 14)),
            ),
            const SizedBox(width: 6),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: isUser ? AppColors.primary : AppColors.grey100,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(18),
                  topRight: const Radius.circular(18),
                  bottomLeft: Radius.circular(isUser ? 18 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 18),
                ),
              ),
              child: Text(
                message.content,
                style: TextStyle(
                  color: isUser ? Colors.white : AppColors.grey600,
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TypingIndicator extends StatelessWidget {
  const _TypingIndicator();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          CircleAvatar(
            radius: 14,
            backgroundColor: AppColors.primary,
            child: const Text('🥕', style: TextStyle(fontSize: 14)),
          ),
          const SizedBox(width: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: AppColors.grey100,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(18),
                topRight: Radius.circular(18),
                bottomRight: Radius.circular(18),
                bottomLeft: Radius.circular(4),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(
                3,
                (i) => _Dot(delay: Duration(milliseconds: i * 150)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Dot extends StatefulWidget {
  final Duration delay;
  const _Dot({required this.delay});

  @override
  State<_Dot> createState() => _DotState();
}

class _DotState extends State<_Dot> with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 600))
      ..repeat(reverse: true);
    _anim = Tween(begin: 0.0, end: -6.0).animate(
      CurvedAnimation(
        parent: _ctrl,
        curve: Interval(widget.delay.inMilliseconds / 600, 1.0, curve: Curves.easeInOut),
      ),
    );
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _anim,
      builder: (_, __) => Transform.translate(
        offset: Offset(0, _anim.value),
        child: Container(
          width: 6,
          height: 6,
          margin: const EdgeInsets.symmetric(horizontal: 2),
          decoration: const BoxDecoration(
            color: AppColors.grey400,
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }
}

class _InputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool loading;
  final VoidCallback onSend;

  const _InputBar({
    required this.controller,
    required this.loading,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        left: 12,
        right: 12,
        top: 8,
        bottom: MediaQuery.of(context).padding.bottom + 8,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: AppColors.grey200)),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              enabled: !loading,
              decoration: InputDecoration(
                hintText: '질문을 입력하세요...',
                hintStyle: const TextStyle(color: AppColors.grey400, fontSize: 14),
                filled: true,
                fillColor: AppColors.grey100,
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
              ),
              style: const TextStyle(fontSize: 14),
              onSubmitted: (_) => onSend(),
              textInputAction: TextInputAction.send,
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: loading ? null : onSend,
            child: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: loading ? AppColors.grey400 : AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.arrow_upward, color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }
}
