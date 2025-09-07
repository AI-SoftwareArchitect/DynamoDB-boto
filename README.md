# DynamoDB-boto
DynamoDB-boto

## Sanal Ortamı Oluşturun:
Projenizin bulunduğu dizinde, venv adında yeni bir sanal ortam oluşturmak için bu komutu çalıştırın.

PowerShell

python -m venv venv
Sanal Ortamı Etkinleştirin:
## Şimdi, oluşturduğunuz sanal ortamı etkinleştirin. Bu, bundan sonra çalıştıracağınız komutların bu ortamdaki Python'ı kullanmasını sağlayacaktır.

PowerShell

.\venv\Scripts\Activate
## Komutu çalıştırdıktan sonra terminal satırınızın başında (venv) yazdığını göreceksiniz. Bu, sanal ortamın etkin olduğunu gösterir.

Gereksinimleri Kurun:
## Sanal ortam etkin durumdayken, Flask ve boto3 paketlerini sorunsuz bir şekilde kurabilirsiniz.

PowerShell

pip install Flask boto3
Uygulamayı Çalıştırın:
Artık tüm paketler doğru ortama yüklendiğine göre, uygulamayı önceki gibi çalıştırabilirsiniz.

PowerShell

$env:LOCAL_DYNAMODB = "true"; python main.py
Bu adımları tamamladıktan sonra, ModuleNotFoundError hatasını almayacak ve uygulamanın yerel DynamoDB emülatörüne başarıyla bağlanmasını sağlayacaksınız.
