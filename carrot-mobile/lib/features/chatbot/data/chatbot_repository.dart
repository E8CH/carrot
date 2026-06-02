import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

class ChatbotRepository {
  final ApiClient _client;
  const ChatbotRepository(this._client);

  Future<String> chat(String message) async {
    final result = await _client.post(
      ApiEndpoints.ragChat,
      body: {'message': message},
    );
    return (result as Map<String, dynamic>)['answer'] as String;
  }
}
