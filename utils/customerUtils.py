from django.db.models import Q

from cinarspa_models.models import Musteri


def try_fetch(musteri_id, musteri_isim, musteri_soyisim, musteri_email, musteri_telefon):
    if (musteri_id is not None):
        return Musteri.objects.filter(id=musteri_id)[0]
    elif (musteri_isim is not None and musteri_soyisim is not None):
        musteriObj, isNew = Musteri.objects.get_or_create(isim=musteri_isim, soyisim=musteri_soyisim)
        if isNew:
            musteriObj.email = musteri_email
            musteriObj.tel = musteri_telefon
            musteriObj.save()
        return musteriObj
    else:
        return None
