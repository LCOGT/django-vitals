from django.views.generic import View
from django.http import JsonResponse

from .conf import conf


def run_checks(checks_to_run=None):
    if not checks_to_run:
        checks_to_run = conf.enabled_checks

    failed = {}
    ok = []

    for c in checks_to_run:
        check = conf.enabled_checks[c]
        inst = check['class'](name=c, **check['args'])
        inst.run_check()
        if inst.errors:
            failed[inst.name] = inst.errors
        else:
            ok.append(inst.name)

    return {'ok': ok, 'failed': failed}


class VitalsJSONView(View):
    def get(self, request):
        checks_to_run = request.GET.get('checks', '').split(',')
        checks_to_run = list(filter(len, checks_to_run))  # filter empty string
        results = run_checks(checks_to_run)
        if results['failed']:
            status = 500
        else:
            status = 200

        return JsonResponse(results, status=status)
