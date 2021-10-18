import click

from hotel_website import create_app
from hotel_website.models import db

app = create_app()

@app.cli.command()
def createdb():
    db.create_all()
    click.echo("All tables created.")


# @app.cli.command()
# def filldb():
#     pass


if __name__ == "__main__":
    app.run(debug=True)