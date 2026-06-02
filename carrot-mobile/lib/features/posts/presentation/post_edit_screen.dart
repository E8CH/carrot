import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import '../../../core/api/api_endpoints.dart';
import '../../../core/providers/api_client_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../data/posts_repository.dart';

class PostEditScreen extends ConsumerStatefulWidget {
  final int postId;
  const PostEditScreen({super.key, required this.postId});

  @override
  ConsumerState<PostEditScreen> createState() => _PostEditScreenState();
}

class _PostEditScreenState extends ConsumerState<PostEditScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  final _priceCtrl = TextEditingController();
  final _tradePlaceCtrl = TextEditingController();

  List<String> _existingPhotos = [];
  final List<XFile> _newImages = [];
  bool _isFree = false;
  bool _loading = true;
  bool _submitting = false;
  String _error = '';

  static const _maxBytes = 5 * 1024 * 1024;
  static const _maxPhotos = 10;

  @override
  void initState() {
    super.initState();
    _loadPost();
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _descCtrl.dispose();
    _priceCtrl.dispose();
    _tradePlaceCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadPost() async {
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      final post = await repo.getPost(widget.postId);
      if (!mounted) return;
      setState(() {
        _titleCtrl.text = post['title'] as String? ?? '';
        _descCtrl.text = post['description'] as String? ?? '';
        _isFree = post['is_free'] as bool? ?? false;
        final price = post['price'];
        if (price != null) _priceCtrl.text = price.toString();
        _tradePlaceCtrl.text = post['trade_place'] as String? ?? '';
        _existingPhotos = ((post['photos'] as List?)?.cast<String>()) ?? [];
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _error = '게시글을 불러올 수 없습니다.'; _loading = false; });
    }
  }

  Future<void> _pickImages() async {
    final picker = ImagePicker();
    final picked = await picker.pickMultiImage(imageQuality: 90);
    if (picked.isEmpty) return;

    final oversized = <String>[];
    for (final img in picked) {
      final size = await img.length();
      if (size > _maxBytes) oversized.add(img.name);
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
    final totalCount = _existingPhotos.length + _newImages.length + picked.length;
    final allowed = picked.take(_maxPhotos - _existingPhotos.length - _newImages.length).toList();
    final showLimitWarning = totalCount > _maxPhotos;
    setState(() { _newImages.addAll(allowed); });
    if (showLimitWarning && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('사진은 최대 $_maxPhotos장까지 선택할 수 있습니다.')),
      );
    }
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
    final supabaseBase = Uri.parse(uploadUrl).origin;
    return '$supabaseBase/storage/v1/object/public/posts/$filePath';
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final totalPhotos = _existingPhotos.length + _newImages.length;
    if (totalPhotos == 0) {
      setState(() => _error = '사진을 1장 이상 선택해주세요.');
      return;
    }
    setState(() { _submitting = true; _error = ''; });
    try {
      final uploadedUrls = <String>[];
      for (final img in _newImages) {
        uploadedUrls.add(await _uploadFile(img));
      }
      final photos = [..._existingPhotos, ...uploadedUrls];
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      await repo.updatePost(widget.postId, {
        'title': _titleCtrl.text.trim(),
        'description': _descCtrl.text.trim(),
        'price': _isFree ? null : int.tryParse(_priceCtrl.text),
        'is_free': _isFree,
        'trade_place': _tradePlaceCtrl.text.trim().isNotEmpty ? _tradePlaceCtrl.text.trim() : null,
        'photos': photos,
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('수정됐어요!')));
        Navigator.of(context).pop();
      }
    } catch (e) {
      setState(() => _error = '수정에 실패했습니다.');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (_error.isNotEmpty && !_submitting && _existingPhotos.isEmpty) {
      return Scaffold(appBar: AppBar(), body: Center(child: Text(_error, style: const TextStyle(color: Colors.red))));
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('게시글 수정'),
        actions: [
          TextButton(
            onPressed: _submitting ? null : _submit,
            child: Text('완료', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 사진
            SizedBox(
              height: 100,
              child: ListView(
                scrollDirection: Axis.horizontal,
                children: [
                  ..._existingPhotos.asMap().entries.map((e) => _ExistingPhotoPreview(
                        url: e.value,
                        onRemove: () => setState(() => _existingPhotos.removeAt(e.key)),
                      )),
                  ..._newImages.asMap().entries.map((e) => _NewImagePreview(
                        file: e.value,
                        onRemove: () => setState(() => _newImages.removeAt(e.key)),
                      )),
                  if (_existingPhotos.length + _newImages.length < _maxPhotos)
                    GestureDetector(
                      onTap: _pickImages,
                      child: Container(
                        width: 80, height: 80,
                        margin: const EdgeInsets.only(right: 8),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.add_photo_alternate_outlined, color: Colors.grey),
                            Text('${_existingPhotos.length + _newImages.length}/$_maxPhotos',
                                style: const TextStyle(fontSize: 11, color: Colors.grey)),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
            const Divider(),
            TextFormField(
              controller: _titleCtrl,
              maxLength: 100,
              decoration: const InputDecoration(hintText: '글 제목', border: InputBorder.none, counterText: ''),
              validator: (v) => (v == null || v.trim().isEmpty) ? '제목을 입력하세요.' : null,
            ),
            const Divider(),
            Row(children: [
              Checkbox(value: _isFree, onChanged: (v) => setState(() => _isFree = v ?? false)),
              const Text('나눔하기'),
            ]),
            if (!_isFree)
              TextFormField(
                controller: _priceCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(hintText: '가격 (원)', border: InputBorder.none),
              ),
            const Divider(),
            TextFormField(
              controller: _descCtrl,
              maxLines: 6,
              decoration: const InputDecoration(hintText: '물품에 대해 자세히 설명해주세요.', border: InputBorder.none),
              validator: (v) => (v == null || v.trim().isEmpty) ? '설명을 입력하세요.' : null,
            ),
            const Divider(),
            TextFormField(
              controller: _tradePlaceCtrl,
              decoration: const InputDecoration(hintText: '거래 희망 장소 (선택)', border: InputBorder.none),
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
    );
  }
}

class _ExistingPhotoPreview extends StatelessWidget {
  final String url;
  final VoidCallback onRemove;
  const _ExistingPhotoPreview({required this.url, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    return Stack(children: [
      Container(
        width: 80, height: 80,
        margin: const EdgeInsets.only(right: 8),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(8),
          image: DecorationImage(image: NetworkImage(url), fit: BoxFit.cover),
        ),
      ),
      Positioned(
        top: 0, right: 4,
        child: GestureDetector(
          onTap: onRemove,
          child: Container(
            width: 18, height: 18,
            decoration: const BoxDecoration(color: Colors.black54, shape: BoxShape.circle),
            child: const Icon(Icons.close, size: 12, color: Colors.white),
          ),
        ),
      ),
    ]);
  }
}

class _NewImagePreview extends StatefulWidget {
  final XFile file;
  final VoidCallback onRemove;
  const _NewImagePreview({required this.file, required this.onRemove});

  @override
  State<_NewImagePreview> createState() => _NewImagePreviewState();
}

class _NewImagePreviewState extends State<_NewImagePreview> {
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
      builder: (ctx, snap) {
        if (!snap.hasData) return const SizedBox(width: 80);
        return Stack(children: [
          Container(
            width: 80, height: 80,
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
            top: 0, right: 4,
            child: GestureDetector(
              onTap: widget.onRemove,
              child: Container(
                width: 18, height: 18,
                decoration: const BoxDecoration(color: Colors.orange, shape: BoxShape.circle),
                child: const Icon(Icons.close, size: 12, color: Colors.white),
              ),
            ),
          ),
        ]);
      },
    );
  }
}
