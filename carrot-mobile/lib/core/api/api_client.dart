import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api_endpoints.dart';

class ApiClient {
  final String? _token;

  const ApiClient({String? token}) : _token = token; // ignore: prefer_initializing_formals

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<dynamic> get(String path, {Map<String, String>? queryParams}) async {
    var uri = Uri.parse('${ApiEndpoints.baseUrl}$path');
    if (queryParams != null && queryParams.isNotEmpty) {
      uri = uri.replace(queryParameters: queryParams);
    }
    final res = await http.get(uri, headers: _headers);
    return _handleResponse(res);
  }

  Future<dynamic> post(String path, {Map<String, dynamic>? body}) async {
    final res = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}$path'),
      headers: _headers,
      body: body != null ? jsonEncode(body) : null,
    );
    return _handleResponse(res);
  }

  Future<dynamic> patch(String path, {Map<String, dynamic>? body}) async {
    final res = await http.patch(
      Uri.parse('${ApiEndpoints.baseUrl}$path'),
      headers: _headers,
      body: body != null ? jsonEncode(body) : null,
    );
    return _handleResponse(res);
  }

  Future<dynamic> delete(String path) async {
    final res = await http.delete(
      Uri.parse('${ApiEndpoints.baseUrl}$path'),
      headers: _headers,
    );
    return _handleResponse(res);
  }

  dynamic _handleResponse(http.Response res) {
    // 상태코드 먼저 확인: 비-JSON 오류 응답(502 HTML 등) 처리
    if (res.statusCode >= 400) {
      try {
        final decoded = jsonDecode(utf8.decode(res.bodyBytes));
        final raw = decoded['detail'];
        final detail = raw is List
            ? (raw.isNotEmpty ? raw.first['msg']?.toString() ?? raw.toString() : '알 수 없는 오류')
            : raw?.toString() ?? '알 수 없는 오류가 발생했습니다.';
        throw ApiException(
          statusCode: res.statusCode,
          code: decoded['code']?.toString() ?? 'UNKNOWN',
          detail: detail,
        );
      } on ApiException {
        rethrow;
      } catch (_) {
        throw ApiException(
          statusCode: res.statusCode,
          code: 'SERVER_ERROR',
          detail: '서버 오류가 발생했습니다. (${res.statusCode})',
        );
      }
    }
    return jsonDecode(utf8.decode(res.bodyBytes));
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String code;
  final String detail;

  const ApiException({
    required this.statusCode,
    required this.code,
    required this.detail,
  });

  @override
  String toString() => 'ApiException($statusCode, $code): $detail';
}
