from django.apps import AppConfig


class PollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'

    def ready(self):
        import django.template.base as base
        from django.template.context import RequestContext, RenderContext

        # Python 3.14 compatibility:
        # RequestContext.__copy__ (via Context.new()) only calls BaseContext.__init__,
        # missing request, _processors, _processors_index, render_context, template.
        # Fix __copy__ to preserve all RequestContext-specific attributes.
        original_copy = RequestContext.__copy__
        def patched_copy(self):
            duplicate = original_copy(self)
            for attr in ('request', '_processors', '_processors_index'):
                if hasattr(self, attr) and not hasattr(duplicate, attr):
                    setattr(duplicate, attr, getattr(self, attr))
            if not hasattr(duplicate, 'render_context'):
                duplicate.render_context = getattr(self, 'render_context', RenderContext())
            return duplicate
        RequestContext.__copy__ = patched_copy

        # Safety net: ensure critical attrs exist before bind_template()
        original_render = base.Template.render
        def patched_render(self, context):
            if not hasattr(context, 'template'):
                context.template = None
            if not hasattr(context, 'render_context'):
                context.render_context = RenderContext()
            if not hasattr(context, '_processors'):
                context._processors = ()
            if not hasattr(context, '_processors_index'):
                context._processors_index = len(context.dicts)
            if not hasattr(context, 'request'):
                context.request = getattr(context, 'request', None)
            return original_render(self, context)
        base.Template.render = patched_render

        # Ensure RequestContext.__init__ always works
        original_request_context_init = RequestContext.__init__
        def patched_request_context_init(self, request, dict_=None, processors=None, **kwargs):
            original_request_context_init(self, request, dict_, processors, **kwargs)
            if not hasattr(self, '_processors'):
                self._processors = () if processors is None else tuple(processors)
            if not hasattr(self, '_processors_index'):
                self._processors_index = len(self.dicts)
        RequestContext.__init__ = patched_request_context_init
