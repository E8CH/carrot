import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import '../../../core/api/api_endpoints.dart';
import '../../../core/providers/api_client_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../data/posts_repository.dart';

class PostFormScreen extends ConsumerStatefulWidget {
  const PostFormScreen({super.key});

  @override
  ConsumerState<PostFormScreen> createState() => _PostFormScreenState();
}

class _PostFormScreenState extends ConsumerState<PostFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  final _priceCtrl = TextEditingController();
  final _tradePlaceCtrl = TextEditingController();

  final List<XFile> _images = [];
  bool _isFree = false;
  bool _loading = false;
  bool _draftSaving = false;
  String _error = '';

  static const _maxBytes = 5 * 1024 * 1024; // 5MB
  static const _maxPhotos = 10;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadDraft());
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _descCtrl.dispose();
    _priceCtrl.dispose();
    _tradePlaceCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadDraft() async {
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      final draft = await repo.getDraft();
      if (draft == null || !mounted) return;

      final restore = await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
          title: const Text('이전에 작성 중인 글이 있어요'),
          content: const Text('이어서 작성하시겠어요?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('새로 작성'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: Text('이어서 작성', style: TextStyle(color: AppColors.primary)),
            ),
          ],
        ),
      );

      if (restore == true && mounted) {
        setState(() {
          _titleCtrl.text = draft['title'] as String? ?? '';
          _descCtrl.text = draft['description'] as String? ?? '';
          _isFree = draft['is_free'] as bool? ?? false;
          final price = draft['price'];
          _priceCtrl.text = price != null ? price.toString() : '';
          _tradePlaceCtrl.text = draft['trade_place'] as String? ?? '';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('임시저장 내용을 복원했어요. 사진은 다시 선택해주세요.')),
        );
      }
    } catch (_) {
      // draft 로드 실패는 무음 처리 — 화면 진입을 막으면 안 됨
    }
  }

  Future<void> _saveDraft() async {
    if (_draftSaving) return;
    setState(() => _draftSaving = true);
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      await repo.saveDraft(
        title: _titleCtrl.text.trim(),
        description: _descCtrl.text.trim(),
        price: _isFree ? null : int.tryParse(_priceCtrl.text),
        isFree: _isFree,
        tradePlace: _tradePlaceCtrl.text.trim().isNotEmpty ? _tradePlaceCtrl.text.trim() : null,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('임시저장됐어요!')),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('임시저장에 실패했습니다.')),
        );
      }
    } finally {
      if (mounted) setState(() => _draftSaving = false);
    }
  }

  Future<void> _pickImages() async {
    final picker = ImagePicker();
    final picked = await picker.pickMultiImage(imageQuality: 90);
    if (picked.isEmpty) return;

    // 초과 파일이 1개라도 있으면 전체 배치 거부 (Web과 동일 동작, AC-4)
    final oversized = <String>[];
    for (final img in picked) {
      final bytes = await img.readAsBytes();
      if (bytes.length > _maxBytes) oversized.add(img.name);
    }

    if (oversized.isNotEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('5MB 초과 파일이 있어 전체 선택이 취소됐습니다: ${oversized.join(', ')}')),
        );
      }
      return;
    }

    if (!mounted) return;
    setState(() {
      final combined = [..._images, ...picked];
      _images
        ..clear()
        ..addAll(combined.take(_maxPhotos));
    });
  }

  Future<String> _uploadFile(XFile file) async {
    final client = ref.read(apiClientProvider);
    final repo = PostsRepository(client);
    final result = await repo.getUploadUrl();
    final uploadUrl = result['upload_url'] as String;
    final filePath = result['file_path'] as String;

    final bytes = await file.readAsBytes();
    final contentType = file.mimeType ?? 'image/jpeg';
    final response = await http.put(
      Uri.parse(uploadUrl),
      body: bytes,
      headers: {'Content-Type': contentType},
    );
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('이미지 업로드 실패 (${response.statusCode})');
    }

    return '${ApiEndpoints.supabaseUrl}/storage/v1/object/public/posts/$filePath';
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_images.isEmpty) {
      setState(() => _error = '사진을 1장 이상 선택해주세요.');
      return;
    }

    setState(() {
      _loading = true;
      _error = '';
    });

    try {
      final photoUrls = <String>[];
      for (final img in _images) {
        final url = await _uploadFile(img);
        photoUrls.add(url);
      }

      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      await repo.createPost(
        title: _titleCtrl.text.trim(),
        description: _descCtrl.text.trim(),
        price: _isFree ? null : int.tryParse(_priceCtrl.text),
        isFree: _isFree,
        tradePlace: _tradePlaceCtrl.text.trim().isNotEmpty ? _tradePlaceCtrl.text.trim() : null,
        photos: photoUrls,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('등록됐어요! 🎉')),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      setState(() => _error = '게시글 등록에 실패했습니다.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        final nav = Navigator.of(context);
        final action = await showDialog<String>(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('작성 중인 글이 있어요'),
            content: const Text('임시저장할까요?'),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx, 'cancel'), child: const Text('취소')),
              TextButton(onPressed: () => Navigator.pop(ctx, 'discard'), child: const Text('저장 안 함')),
              TextButton(
                onPressed: () => Navigator.pop(ctx, 'save'),
                child: Text('저장 후 나가기', style: TextStyle(color: AppColors.primary)),
              ),
            ],
          ),
        );
        if (!mounted) return;
        if (action == 'save') {
          await _saveDraft();
          if (mounted) nav.pop();
        } else if (action == 'discard') {
          nav.pop();
        }
        // 'cancel' → 아무것도 하지 않음
      },
      child: Stack(
        children: [
          Scaffold(
          appBar: AppBar(
        title: const Text('내 물건 팔기'),
        actions: [
          TextButton(
            onPressed: (_draftSaving || _loading) ? null : _saveDraft,
            child: Text('임시저장', style: TextStyle(color: AppColors.primary.withValues(alpha: (_draftSaving || _loading) ? 0.4 : 1.0))),
          ),
          TextButton(
            onPressed: _loading ? null : _submit,
            child: Text('완료', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 사진 선택
            SizedBox(
              height: 100,
              child: ListView(
                scrollDirection: Axis.horizontal,
                children: [
                  GestureDetector(
                    onTap: _pickImages,
                    child: Container(
                      width: 80,
                      height: 80,
                      margin: const EdgeInsets.only(right: 8),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey.shade300),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.camera_alt_outlined, color: Colors.grey),
                          Text('${_images.length}/$_maxPhotos',
                              style: const TextStyle(fontSize: 11, color: Colors.grey)),
                        ],
                      ),
                    ),
                  ),
                  ..._images.asMap().entries.map((e) => _ImagePreview(
                        file: e.value,
                        onRemove: () => setState(() => _images.removeAt(e.key)),
                      )),
                ],
              ),
            ),
            const Divider(),

            // 제목
            TextFormField(
              controller: _titleCtrl,
              maxLength: 100,
              decoration: const InputDecoration(
                hintText: '글 제목',
                border: InputBorder.none,
                counterText: '',
              ),
              validator: (v) => (v == null || v.trim().isEmpty) ? '제목을 입력하세요.' : null,
            ),
            const Divider(),

            // 가격
            Row(
              children: [
                Checkbox(value: _isFree, onChanged: (v) => setState(() => _isFree = v ?? false)),
                const Text('나눔하기'),
              ],
            ),
            if (!_isFree)
              TextFormField(
                controller: _priceCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(hintText: '가격 (원)', border: InputBorder.none),
              ),
            const Divider(),

            // 설명
            TextFormField(
              controller: _descCtrl,
              maxLines: 6,
              decoration: const InputDecoration(
                hintText: '물품에 대해 자세히 설명해주세요.',
                border: InputBorder.none,
              ),
              validator: (v) => (v == null || v.trim().isEmpty) ? '설명을 입력하세요.' : null,
            ),
            const Divider(),

            // 거래 희망 장소
            TextFormField(
              controller: _tradePlaceCtrl,
              decoration: const InputDecoration(
                hintText: '거래 희망 장소 (선택)',
                border: InputBorder.none,
              ),
            ),
            const Divider(),

            if (_error.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(_error, style: const TextStyle(color: Colors.red, fontSize: 13)),
              ),
          ],
        ),
      ),
          ),  // Scaffold
          if (_loading)
            Container(
              color: Colors.white.withValues(alpha: 0.8),
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 12),
                    Text('등록 중...', style: TextStyle(fontSize: 14, color: Colors.grey)),
                  ],
                ),
              ),
            ),
        ],
      ),  // Stack
    );  // PopScope
  }
}

class _ImagePreview extends StatefulWidget {
  final XFile file;
  final VoidCallback onRemove;
  const _ImagePreview({required this.file, required this.onRemove});

  @override
  State<_ImagePreview> createState() => _ImagePreviewState();
}

class _ImagePreviewState extends State<_ImagePreview> {
  late final Future<Uint8List> _bytesFuture;

  @override
  void initState() {
    super.initState();
    _bytesFuture = widget.file.readAsBytes();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Uint8List>(
      future: _bytesFuture,
      builder: (context, snap) {
        if (!snap.hasData) return const SizedBox(width: 80);
        return Stack(
          children: [
            Container(
              width: 80,
              height: 80,
              margin: const EdgeInsets.only(right: 8),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                image: DecorationImage(
                  image: MemoryImage(snap.data!),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            Positioned(
              top: 0,
              right: 4,
              child: GestureDetector(
                onTap: widget.onRemove,
                child: Container(
                  width: 18,
                  height: 18,
                  decoration: const BoxDecoration(color: Colors.black54, shape: BoxShape.circle),
                  child: const Icon(Icons.close, size: 12, color: Colors.white),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
