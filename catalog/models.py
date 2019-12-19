from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date


# Create your models here
class Genre(models.Model):
    """model representing a book genre"""
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g Science fiction)')

    def __str__(self):
        """string for representing the model object"""
        return self.name

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)        

    # foreign key used because book can only one author , but authors can have multiple books
    # Author as a string rather than object because it has'nt been declared yet in the file
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    #ManyToManyField used because genre can contain many books. books can cover many genres
    #Genre class has already been defined so we can specify the object above
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """string for representing the model object"""
        return self.title

    def get_absolute_url(self):
        """returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """create a string for the genre, this is required to display the genre in admin ."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    display_genre.short_description = 'Genre'        

class BookInstance(models.Model):
    """model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across while library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


    LOAN_STATUS = (
        ('m', 'Maintainance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length = 1,
        choices = LOAN_STATUS,
        blank = True,
        default = 'm',
        help_text = 'Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """string for representing the Model object."""
        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False    




class Author(models.Model):
    """model representing an author"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """string for representing the model object."""
        return f'{self.last_name}, {self.first_name}' 


class Language(models.Model):
    """model representing a language (e.g. english, french, japanese, etc.)"""
    name  = models.CharField(max_length=200, help_text='Enter the book\'s natural language(e.g. English, French, Japanese etc.)')

    def __str__(self):
        return self.name        


