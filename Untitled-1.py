
        if (request.user.is_superuser):
            return Response(makeArraySerialization(Randevu.objects.all())
        elif (request.user.is_staff is True):
            return Response(makeArraySerialization(Randevu.objects.all())