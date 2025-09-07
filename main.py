import os
import json
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify

# Flask uygulamasını başlat
app = Flask(__name__)

# DynamoDB'ye bağlanma
# Eğer bir çevre değişkeni olarak 'LOCAL_DYNAMODB' tanımlıysa,
# yerel emülatöre bağlan. Aksi halde, AWS kimlik bilgileriyle bağlanmayı dener.
# Buradaki ayarlar yerel emülatör için özeldir.
if os.environ.get('LOCAL_DYNAMODB') == 'true':
    print("Yerel DynamoDB emülatörüne bağlanılıyor.")
    DYNAMODB_CLIENT = boto3.client(
        'dynamodb',
        endpoint_url='http://localhost:8000',
        region_name='us-east-1',
        aws_access_key_id='DUMMYID',
        aws_secret_access_key='DUMMYKEY'
    )
    DYNAMODB_RESOURCE = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8000',
        region_name='us-east-1',
        aws_access_key_id='DUMMYID',
        aws_secret_access_key='DUMMYKEY'
    )
else:
    print("Standart AWS DynamoDB'ye bağlanılıyor.")
    DYNAMODB_CLIENT = boto3.client('dynamodb')
    DYNAMODB_RESOURCE = boto3.resource('dynamodb')

TABLE_NAME = 'MyItems'

def create_table_if_not_exists():
    """
    Uygulama başladığında DynamoDB tablosunun varlığını kontrol eder
    ve yoksa oluşturur.
    """
    try:
        DYNAMODB_CLIENT.describe_table(TableName=TABLE_NAME)
        print(f"'{TABLE_NAME}' tablosu zaten mevcut.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"'{TABLE_NAME}' tablosu bulunamadı, oluşturuluyor...")
            DYNAMODB_RESOURCE.create_table(
                TableName=TABLE_NAME,
                KeySchema=[
                    {'AttributeName': 'itemId', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'itemId', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print(f"'{TABLE_NAME}' tablosu başarıyla oluşturuldu.")
        else:
            print(f"Hata: {e.response['Error']['Code']}")

# Uygulama başlatıldığında tabloyu oluştur
with app.app_context():
    create_table_if_not_exists()

@app.route('/')
def index():
    """
    Ön yüzü render eden ana sayfa.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Yerel DynamoDB Uygulaması</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
                color: #333;
            }
            form {
                display: flex;
                margin-bottom: 20px;
            }
            input[type="text"] {
                flex-grow: 1;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-right: 10px;
            }
            button {
                padding: 10px 15px;
                border: none;
                background-color: #5cb85c;
                color: white;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #4cae4c;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                padding: 10px;
                background-color: #eee;
                border-radius: 4px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .delete-btn {
                background-color: #d9534f;
                padding: 5px 10px;
            }
            .delete-btn:hover {
                background-color: #c9302c;
            }
            #message {
                text-align: center;
                margin-top: 15px;
                color: red;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DynamoDB Öğeleri</h1>
            <form id="addItemForm">
                <input type="text" id="itemInput" placeholder="Öğe adını girin..." required>
                <button type="submit">Ekle</button>
            </form>
            <ul id="itemsList">
                <!-- Öğeler buraya yüklenecek -->
            </ul>
            <p id="message"></p>
        </div>

        <script>
            const form = document.getElementById('addItemForm');
            const itemInput = document.getElementById('itemInput');
            const itemsList = document.getElementById('itemsList');
            const messageEl = document.getElementById('message');

            // API'den öğeleri alıp listeyi günceller
            async function fetchItems() {
                try {
                    const response = await fetch('/items');
                    if (!response.ok) throw new Error('Öğeler yüklenemedi.');
                    const items = await response.json();
                    itemsList.innerHTML = '';
                    if (items.length === 0) {
                        itemsList.innerHTML = '<li>Henüz öğe yok.</li>';
                    } else {
                        items.forEach(item => {
                            const li = document.createElement('li');
                            li.innerHTML = `<span>${item.itemId}</span>
                                            <button class="delete-btn" data-id="${item.itemId}">Sil</button>`;
                            itemsList.appendChild(li);
                        });
                    }
                } catch (error) {
                    console.error('Hata:', error);
                    messageEl.textContent = 'Öğeler alınırken bir hata oluştu.';
                }
            }

            // Form gönderildiğinde yeni öğe ekler
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const newItemId = itemInput.value.trim();
                if (!newItemId) return;

                try {
                    const response = await fetch('/items', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ itemId: newItemId })
                    });

                    const result = await response.json();
                    if (!response.ok) throw new Error(result.error || 'Öğe eklenemedi.');

                    itemInput.value = '';
                    messageEl.textContent = 'Öğe başarıyla eklendi.';
                    fetchItems();
                } catch (error) {
                    console.error('Hata:', error);
                    messageEl.textContent = error.message;
                }
            });

            // "Sil" butonuna tıklandığında öğeyi siler
            itemsList.addEventListener('click', async (e) => {
                if (e.target.classList.contains('delete-btn')) {
                    const itemId = e.target.dataset.id;
                    try {
                        const response = await fetch(`/items/${itemId}`, {
                            method: 'DELETE'
                        });

                        const result = await response.json();
                        if (!response.ok) throw new Error(result.error || 'Öğe silinemedi.');

                        messageEl.textContent = 'Öğe başarıyla silindi.';
                        fetchItems();
                    } catch (error) {
                        console.error('Hata:', error);
                        messageEl.textContent = error.message;
                    }
                }
            });

            // Sayfa yüklendiğinde öğeleri getir
            document.addEventListener('DOMContentLoaded', fetchItems);
        </script>
    </body>
    </html>
    """
    return html_content

@app.route('/items', methods=['GET'])
def get_items():
    """
    DynamoDB'deki tüm öğeleri getirir.
    """
    try:
        table = DYNAMODB_RESOURCE.Table(TABLE_NAME)
        response = table.scan()
        return jsonify(response.get('Items', []))
    except ClientError as e:
        print(f"Hata: {e.response['Error']['Code']}")
        return jsonify({"error": "Öğeler alınırken bir hata oluştu."}), 500

@app.route('/items', methods=['POST'])
def add_item():
    """
    Yeni bir öğe ekler.
    """
    try:
        data = request.get_json()
        if not data or 'itemId' not in data:
            return jsonify({"error": "Geçersiz istek. 'itemId' gereklidir."}), 400

        item_id = data['itemId']
        table = DYNAMODB_RESOURCE.Table(TABLE_NAME)
        table.put_item(
            Item={'itemId': item_id}
        )
        return jsonify({"message": "Öğe başarıyla eklendi.", "itemId": item_id}), 201
    except ClientError as e:
        print(f"Hata: {e.response['Error']['Code']}")
        return jsonify({"error": "Öğe eklenirken bir hata oluştu."}), 500

@app.route('/items/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Belirli bir öğeyi siler.
    """
    try:
        table = DYNAMODB_RESOURCE.Table(TABLE_NAME)
        table.delete_item(
            Key={'itemId': item_id}
        )
        return jsonify({"message": f"'{item_id}' adlı öğe başarıyla silindi."}), 200
    except ClientError as e:
        print(f"Hata: {e.response['Error']['Code']}")
        return jsonify({"error": "Öğe silinirken bir hata oluştu."}), 500

if __name__ == '__main__':
    # Flask uygulamasını başlatmadan önce DynamoDB tablosunu kontrol et
    # Eğer bu satırın altındaki kod çalışmıyorsa
    # `pip install Flask boto3` komutunu çalıştırmanız gerekir.
    app.run(debug=True, port=5000)
