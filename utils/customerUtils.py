from django.db.models import Q

from cinarspa_models.models import Musteri


def try_fetch(musteri_id, musteri_isim, musteri_soyisim, musteri_email, musteri_telefon,save=True):


    if (musteri_id is not None or musteri_id != ""):
        musteriler = Musteri.objects.filter(id=musteri_id)
        if (musteriler.count()>0):
            return musteriler[0]

    if musteri_isim is not None and musteri_soyisim is not None:
        if save is True:
            musteriObj, isNew = Musteri.objects.get_or_create(
                    isim=musteri_isim,
                    soyisim=musteri_soyisim,
                    tel=musteri_telefon)
            if isNew:
                musteriObj.email = musteri_email
                musteriObj.save()
            return musteriObj
        else:
            gelenMusteriler = Musteri.objects.filter(isim=musteri_isim, soyisim=musteri_soyisim,
                                                tel=musteri_telefon)
            if gelenMusteriler.count() > 0:
                return gelenMusteriler[0]
            else:
                return None

    return None
