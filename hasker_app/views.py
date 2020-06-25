from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views import generic

from hasker_app.form import UserForm, UserEditForm, QuestionForm
from hasker_app.models import Question, UserRate, UserReq, Answer, Tag


_side_question_queryset = (
    Question
    .objects
    .annotate(rate=Coalesce(Sum('rates__rate'), 0))
    .order_by('-rate', '-created_date')[0:10]
)


def for_authenticated_users(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Need to authenticate first!')
        return func(request, *args, **kwargs)

    return wrapper


class SidePanelView(generic.ListView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['side_questions'] = _side_question_queryset.all()
        return context


class QuestionView(SidePanelView):
    queryset = Answer.objects.annotate(rate=Coalesce(Sum('rates__rate'), 0))
    template_name = 'hasker_app/question.html'

    def get_queryset(self):
        self.queryset = (
            Answer
            .objects
            .annotate(rate=Coalesce(Sum('rates__rate'), 0))
            .filter(question=self.kwargs['pk'])
            .order_by('-confirmed', '-rate', '-created_date')
        )
        return super().get_queryset()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['question'] = (
            Question
            .objects
            .annotate(rate=Coalesce(Sum('rates__rate'), 0))
            .get(id=self.kwargs['pk'])
        )
        return context


class QuestionListView(SidePanelView):
    queryset = Question.objects.annotate(rate=Coalesce(Sum('rates__rate'), 0))
    paginate_by = 10
    template_name = 'hasker_app/question_list.html'
    header_type = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.header_type:
            context['header_type'] = self.header_type
        return context


class QuestionDateOrderedListView(QuestionListView):
    ordering = ['-created_date', '-rate']
    header_type = 'date'


class QuestionRateOrderedListView(QuestionListView):
    ordering = ['-rate', '-created_date']
    header_type = 'rate'


class QuestionSearchListView(QuestionRateOrderedListView):
    header_type = 'sorted'

    def get_queryset(self):
        if 'search_tag' in self.request.GET.keys():
            self.queryset = (
                super()
                .queryset
                .filter(
                    tags__name=self.request.GET['search_tag']
                )
            )
        else:
            self.queryset = (
                super()
                .queryset
                .filter(
                    Q(label__contains=self.request.GET['search_str']) |
                    Q(text__contains=self.request.GET['search_str'])
                )
            )
        return super().get_queryset()


@for_authenticated_users
def post_answer(request, question_id):
    if Question.objects.filter(id=question_id).count() == 0:
        raise Http404('No question found')
    answer = Answer(
        text=request.POST['text'],
        question_id=question_id,
        user=UserReq.objects.get(user=request.user)
    )
    answer.save()
    return redirect('question_detail', pk=question_id)


def vote_change(user, obj_type, obj_id, value):
    if obj_type == 'question':
        question_id = obj_id
    elif obj_type == 'answer':
        question_id = Answer.objects.get(pk=obj_id).question_id
    else:
        raise Http404('No type found')

    rate_list = UserRate.objects.filter(user__user=user, **{f'{obj_type}__id': obj_id}).all()
    if rate_list:
        rate = rate_list[0]
        # check if current rate and desirable has different sign
        if rate.rate * value > 0:
            return question_id
        rate.rate += value
    else:
        user_req = UserReq.objects.get(user=user)
        rate = UserRate(user=user_req, rate=value, **{f'{obj_type}_id': obj_id})
    rate.save()
    return question_id


@for_authenticated_users
def vote_up(request, obj_type, obj_id):
    question_id = vote_change(request.user, obj_type, obj_id, 1)
    return redirect('question_detail', pk=question_id)


@for_authenticated_users
def vote_down(request, obj_type, obj_id):
    question_id = vote_change(request.user, obj_type, obj_id, -1)
    return redirect('question_detail', pk=question_id)


def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            user_req = UserReq(user=form.instance)
            if 'avatar' in request.FILES.keys():
                user_req.avatar = request.FILES['avatar']
            user_req.save()
            return HttpResponseRedirect('/account/login')
        else:
            pass
    else:
        form = UserForm()

    return render(
        request,
        'hasker_app/register.html',
        {
            'form': form,
            'side_questions': _side_question_queryset.all()
        }
    )


@for_authenticated_users
def edit_user(request):
    if request.method == 'POST':
        user_req = UserReq.objects.get(user__id=request.user.id)
        form = UserEditForm(request.POST, request.FILES)
        if form.is_valid():
            if 'avatar' in request.FILES.keys():
                user_req.avatar = request.FILES['avatar']
            user_req.user.email = form.cleaned_data['email']
            user_req.user.save()
            user_req.save()
    else:
        user_req = UserReq.objects.get(user=request.user)
    form = UserEditForm(initial={'avatar': user_req.avatar, 'email': user_req.user.email})
    return render(
        request,
        'hasker_app/account_edit.html',
        {
            'form': form,
            'side_questions': _side_question_queryset.all()
        }
    )


@for_authenticated_users
def ask_question(request):
    tags = Tag.objects.all()
    tags_list = [x.name for x in tags]
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user.user_req
            form.save()
            return HttpResponseRedirect(f'/question/{form.instance.id}')
    else:
        form = QuestionForm()
    return render(
        request,
        'hasker_app/ask_question.html',
        {
            'form': form,
            'tags_list': tags_list,
            'side_questions': _side_question_queryset.all()
        }
    )
