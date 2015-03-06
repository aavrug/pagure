# -*- coding: utf-8 -*-

"""
 (c) 2015 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

__requires__ = ['SQLAlchemy >= 0.8']
import pkg_resources

import json
import unittest
import shutil
import sys
import os

import pygit2
from mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import progit.lib
import tests


class ProgitFlaskPluginstests(tests.Modeltests):
    """ Tests for flask plugins controller of progit """

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(ProgitFlaskPluginstests, self).setUp()

        progit.APP.config['TESTING'] = True
        progit.SESSION = self.session
        progit.ui.SESSION = self.session
        progit.ui.app.SESSION = self.session
        progit.ui.plugins.SESSION = self.session

        progit.APP.config['GIT_FOLDER'] = tests.HERE
        progit.APP.config['FORK_FOLDER'] = os.path.join(
            tests.HERE, 'forks')
        progit.APP.config['TICKETS_FOLDER'] = os.path.join(
            tests.HERE, 'tickets')
        progit.APP.config['DOCS_FOLDER'] = os.path.join(
            tests.HERE, 'docs')
        self.app = progit.APP.test_client()

    def test_index(self):
        """ Test the index endpoint. """

        output = self.app.get('/foo/settings/Mail')
        self.assertEqual(output.status_code, 302)

        user = tests.FakeUser()
        with tests.user_set(progit.APP, user):
            output = self.app.get('/foo/settings/Mail')
            self.assertEqual(output.status_code, 404)

            tests.create_projects(self.session)

            output = self.app.get('/test/settings/Mail')
            self.assertEqual(output.status_code, 403)

        user = tests.FakeUser(username='pingou')
        with tests.user_set(progit.APP, user):
            output = self.app.get('/test/settings/Mail')
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<p>test project #1</p>' in output.data)
            self.assertTrue('<h3>Mail</h3>' in output.data)
            self.assertTrue(
                '<td><label for="mail_to">Mail to '
                '<span class="error">*</span></label></td>'
                in output.data)
            self.assertTrue(
                '<input id="active" name="active" type="checkbox" value="y">'
                in output.data)

            csrf_token = output.data.split(
                'name="csrf_token" type="hidden" value="')[1].split('">')[0]

            data = {
                'mail_to': 'foo@bar',
            }

            output = self.app.post('/test/settings/Mail', data=data)
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<p>test project #1</p>' in output.data)
            self.assertTrue('<h3>Mail</h3>' in output.data)
            self.assertTrue(
                '<td><label for="mail_to">Mail to '
                '<span class="error">*</span></label></td>'
                in output.data)
            self.assertTrue(
                '<input id="active" name="active" type="checkbox" value="y">'
                in output.data)

            data['csrf_token'] = csrf_token
            output = self.app.post('/test/settings/Mail', data=data)
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<p>test project #1</p>' in output.data)
            self.assertTrue('<h3>Mail</h3>' in output.data)
            self.assertTrue(
                '<li class="message">Hook inactived</li>' in output.data)
            self.assertTrue(
                '<td><label for="mail_to">Mail to '
                '<span class="error">*</span></label></td>'
                in output.data)
            self.assertTrue(
                '<input id="active" name="active" type="checkbox" value="y">'
                in output.data)

            data['csrf_token'] = csrf_token
            data['active'] = 'y'
            # No git found
            output = self.app.post('/test/settings/Mail', data=data)
            self.assertEqual(output.status_code, 404)

            tests.create_projects_git(tests.HERE)

            # With the git and all
            output = self.app.post('/test/settings/Mail', data=data)
            self.assertTrue('<p>test project #1</p>' in output.data)
            self.assertTrue('<h3>Mail</h3>' in output.data)
            self.assertTrue(
                '<li class="message">Hook activated</li>' in output.data)
            self.assertTrue(
                '<td><label for="mail_to">Mail to '
                '<span class="error">*</span></label></td>'
                in output.data)
            self.assertTrue(
                '<input checked id="active" name="active" type="checkbox" '
                'value="y">' in output.data)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(ProgitFlaskPluginstests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)