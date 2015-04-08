from flask.ext.wtf import Form
from wtforms import SelectField


class SubmitForm(Form):
    group = SelectField('group', choices=[('', ''), ('rutgers', 'Rutgers'), ('hh', 'Hackathon Hackers')])

    def validate(self):
        print self.group.data
        if self.group.data not in ['rutgers', 'hh']:
            return False
        return True