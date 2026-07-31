from getpass import getpass
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()

sifre = getpass("Yönetici şifresini girin: ")
sifre_tekrar = getpass("Şifreyi tekrar girin: ")

if not sifre:
    print("Şifre boş olamaz.")

elif sifre != sifre_tekrar:
    print("Şifreler aynı değil.")

else:
    olusturulan_hash = password_hash.hash(sifre)

    print("\nOluşturulan şifre hash'i:")
    print(olusturulan_hash)