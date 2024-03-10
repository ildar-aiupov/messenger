# Generated by Django 4.2.10 on 2024-03-08 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("v1", "0004_alter_mailing_tag"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=200, unique=True, verbose_name="Тэг"),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="client",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="v1.tag",
                to_field="name",
                verbose_name="Тэг",
            ),
        ),
        migrations.AlterField(
            model_name="mailing",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="v1.tag",
                to_field="name",
                verbose_name="Тэг",
            ),
        ),
    ]
