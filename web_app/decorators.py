
def request_resolver(func):
	def _wrapped_view(request, *args, **kwargs):
		if 'dev' in request.path:
			kwargs['report_type'] = 'dummy'
			return func(request, *args, **kwargs)
		else:
			kwargs['report_type'] = 'status'
			return func(request, *args, **kwargs)
	return _wrapped_view