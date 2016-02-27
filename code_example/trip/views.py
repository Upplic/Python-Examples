
@jsonrpc_method('iway1c.v1.trip.put', authenticated=api_iway1c_authenticate)
@transaction.atomic
def put(request, obj):
    """
    создание поездок либо обновление данных о поездках
    """
    Log1CRequest(method='iway1c.v1.trip.put', data=obj).save()
    trip_uids_accept = []
    try:
        for el in obj['trips']:
            trip = TripBase.get_or_create_from_json(
                el, request.user, req=request)
            if trip:
                trip_uids_accept.append(trip.trip_uid)
    except TypeError as e:
        error = RpcError400
        error.message = '{} {}'.format(error.message, e)
        raise error
    except KeyError as e:
        error = RpcError400
        error.message = '{} KeyError {}'.format(error.message, e)
        raise error

    tasks.new_trip_count.delay()
    count = TripBase.objects.all().count()
    return {'trips': trip_uids_accept, 'count': count}


@jsonrpc_method('web.v1.trip.reset_driver', authenticated=True)
@check_perm_trip
def reset_driver(request, obj):
    """
    сброс предварительно назначенного водителя и автомобиля
    """
    trip_id = obj.get('trip_id', 0)
    disp_id = obj.get('disp_id', None)
    disp = Disp.active.get(id=disp_id)
    try:
        pers = Personal.active.get(user=request.user)
    except Personal.DoesNotExist:
        if not request.user.is_superuser:
            raise RpcError1000
    else:
        if disp not in pers.disps.all():
            raise RpcError1000
    try:
        trip = TripDisp.active.get(id=trip_id, disp=disp)
    except TripDisp.DoesNotExist:
        raise RpcError404
    trip.driver_new = trip.driver
    trip.car_new = trip.car
    trip.save(editor=request.user, action=ACTION_TRIP_RESET_DRIVER)
    tr = trip
    return {
        'driver_id': trip.driver.id if trip.driver else None,
        'car_id': trip.car.id if trip.car else None,
        'is_need_confirm_driver': trip.is_need_confirm_driver(),
        'sms_status': trip.sms_status,
        'mail_status': trip.is_mail_send
    }
