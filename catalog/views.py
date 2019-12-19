import datetime
from django.shortcuts import render, get_object_or_404
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm




# Create your views here.
@login_required
def index(request):
    """view function for the index page"""

    #generate count of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genre = Genre.objects.count()
    num_books_contain = Book.objects.filter(title__icontains='lord').count()

    #available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()


    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre,
        'num_books_contain': num_books_contain,
        'num_visits': num_visits,
    }

    #render the html page template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(LoginRequiredMixin,generic.ListView):
    model = Book  
    paginate_by = 2

class BookDetailView(LoginRequiredMixin,generic.DetailView):
    model = Book

class AuthorListView(LoginRequiredMixin,generic.ListView):
    model = Author

class AuthorDetailView(LoginRequiredMixin,generic.DetailView):
    model = Author        

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back') 

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

@permission_required('catalog.can_mark_returned')
def borrowed(request):
    """view for borrowed books"""
    borrowed_books = BookInstance.objects.filter(status__exact='o')

    context = {
        'borrowed_books': borrowed_books,
    }

    return render(request, 'catalog/all_borrowed.html', context)   


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin,UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookDelete(PermissionRequiredMixin,DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    success_url = reverse_lazy('books')


