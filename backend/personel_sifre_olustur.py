from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()

sifre = "Personel123!"

sifre_hash = password_hash.hash(sifre)

print("Personel şifresi:", sifre)
print("Veritabanına yazılacak hash:")
print(sifre_hash)