from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class User(AbstractUser):
    coin = models.IntegerField(default=0, verbose_name='コイン')

    books = models.ManyToManyField(
        # まだ定義してないので文字列で指定する必要がある
        'Book',
        through='TransactionRecord'
    )

class Category(models.Model):
    display_order = models.IntegerField(verbose_name='表示順')
    name = models.CharField(max_length=80, verbose_name='名前')

    class Meta:
        ordering = ['display_order']

        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ'

    def __str__(self):
        return self.name

class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='カテゴリ')
    title = models.CharField(max_length=80, verbose_name='タイトル')
    abstract = models.TextField(verbose_name='概要')
    price = models.PositiveIntegerField(verbose_name='価格')
    published = models.BooleanField('公開')
    image = models.ImageField(upload_to='book_images/', null=True, blank=True, verbose_name='画像')

    class Meta:
        verbose_name = '書籍'
        verbose_name_plural = '書籍'

    def __str__(self):
        return self.title

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='書籍')
    number = models.PositiveIntegerField(verbose_name='章番号')
    title = models.CharField(max_length=80, verbose_name='章名')
    body = models.TextField(verbose_name='本文')
    def title_with_number(self):
        return f'第{self.number}章 {self.title}'
    def next_chapter(self):
        return self.book.chapter_set.filter(number=self.number+1).first()

    def prev_chapter(self):
        return self.book.chapter_set.filter(number=self.number-1).first()

    class Meta:
        ordering = ['number']

        verbose_name = '章'
        verbose_name_plural = '章'

    def __str__(self):
        return self.title

class TransactionRecord(models.Model):
    class Kind(models.IntegerChoices):
        CHARGE = (1, 'チャージ')
        USE = (2, '使用')

    kind = models.IntegerField(choices=Kind.choices, verbose_name='種類')
    amount = models.PositiveIntegerField(verbose_name='金額')
    # 取引記録がある場合、削除はできなくする
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='ユーザー')
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.PROTECT, verbose_name='書籍')
    datetime = models.DateTimeField(verbose_name='日時')

    class Meta:
        verbose_name = '取引記録'
        verbose_name_plural = '取引記録'

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='書籍')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    rating = models.PositiveIntegerField(verbose_name='評価', default=0)
    comment = models.TextField(verbose_name='コメント', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='投稿日')

    class Meta:
        verbose_name = 'レビュー'
        verbose_name_plural = 'レビュー'
        unique_together = ('book', 'user')  # 同じユーザーが同じ書籍に複数のレビューを投稿できないようにする

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
