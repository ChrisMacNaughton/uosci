import mock
import unittest
import uosci.mojo as mojo


class TestModel(unittest.TestCase):
    def setUp(self):
        super(TestModel, self).setUp()

    @mock.patch.object(mojo, 'execute')
    def test_call_main(self, _execute):
        old_sys_argv = mojo.sys.argv
        mojo.sys.argv = [old_sys_argv[0]] + \
            ['-u', 'test', '-p', 'test-pass']
        try:
            mojo.main()
        finally:
            mojo.argv = old_sys_argv
        _execute.assert_called_with(
            'http://10.245.162.49:8080', 'test', 'test-pass', None)

    @mock.patch.object(mojo, 'execute')
    def test_filter(self, _execute):
        old_sys_argv = mojo.sys.argv
        mojo.sys.argv = [old_sys_argv[0]] + \
            ['-u', 'test', '-p', 'test-pass', '-f', 'test_stuff']
        try:
            mojo.main()
        finally:
            mojo.argv = old_sys_argv
        _execute.assert_called_with(
            'http://10.245.162.49:8080', 'test', 'test-pass', 'test_stuff')

    @mock.patch.object(mojo.uosci_jenkins, 'Jenkins')
    def test_execute(self, _jenkins):
        client = mock.MagicMock()
        _jenkins.return_value = client
        client.matrix.return_value = [{
            'name': 'test'
        }]
        mojo.execute(
            host='http://127.0.0.1:8080',
            username='test_user',
            password='test_password'
        )
        _jenkins.assert_called_with(
            'http://127.0.0.1:8080',
            username='test_user',
            password='test_password')
        client.matrix.assert_called_with('MojoMatrix')

    def test_parser(self):
        args = mojo.parse_args([
            '-u', 'test_user',
            '-p', 'supersecret'])
        self.assertEqual(args.username, 'test_user')
        self.assertEqual(args.password, 'supersecret')
        self.assertEqual(args.host, 'http://10.245.162.49:8080')

    @mock.patch.object(mojo.uosci_jenkins, 'Jenkins')
    def test_execute_with_filter(self, _jenkins):
        client = mock.MagicMock()
        _jenkins.return_value = client
        client.matrix.return_value = [{
            'name': 'testing stuff'
        }]
        mojo.execute(
            host='http://127.0.0.1:8080',
            username=None,
            password=None,
            filter='testing',
        )

    def test_filter_job_name_with_test(self):
        self.assertFalse(mojo.filter_job("test_something"))
        self.assertTrue(mojo.filter_job("not-included"))

    def test_filter_job_name_with_filter(self):
        self.assertFalse(mojo.filter_job("test_something"))
        self.assertTrue(mojo.filter_job("test_something", "else"))

