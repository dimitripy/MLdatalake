import unittest
from unittest.mock import patch, mock_open, MagicMock
from airflow.models import DagBag
import sys
from zip_to_db_dag import run_data_loading

sys.modules['airflow'] = MagicMock()
sys.modules['airflow.models'] = MagicMock()
sys.modules['airflow.operators.python'] = MagicMock()
sys.modules['SQLAlchemy_functions'] = MagicMock()
sys.modules['data_loader'] = MagicMock()
sys.modules['zip_extractor'] = MagicMock()
sys.modules['csv_converter'] = MagicMock()

class TestZipToDbDag(unittest.TestCase):

    def setUp(self):
        self.dagbag = DagBag()
        self.dag_id = 'zip_to_db_dag'
        self.dag = self.dagbag.get_dag(self.dag_id)

    def test_dag_loaded(self):
        self.assertIsNotNone(self.dag)
        self.assertEqual(self.dag.dag_id, self.dag_id)

    def test_task_count(self):
        self.assertEqual(len(self.dag.tasks), 3)

    def test_task_dependencies(self):
        extract_task = self.dag.get_task('extract_zip')
        convert_csv_task = self.dag.get_task('convert_csv_files')
        data_loading_task = self.dag.get_task('load_and_process_data')

        self.assertIn(convert_csv_task, extract_task.downstream_list)
        self.assertIn(data_loading_task, convert_csv_task.downstream_list)

    def test_extract_zip_task(self):
        task = self.dag.get_task('extract_zip')
        self.assertEqual(task.python_callable.__name__, 'main_extract_zip')
        self.assertEqual(task.op_kwargs['config_path'], './config.json')
        self.assertEqual(task.op_kwargs['source_path'], '/home/ageq/Git_Projects/MLdatalake/source')

    def test_convert_csv_task(self):
        task = self.dag.get_task('convert_csv_files')
        self.assertEqual(task.python_callable.__name__, 'main_convert_csv')
        self.assertEqual(task.op_kwargs['extract_to_path'], '/home/ageq/Git_Projects/MLdatalake/source/archive')
        self.assertEqual(task.op_kwargs['output_csv_path'], '/home/ageq/Git_Projects/MLdatalake/source/combined.csv')

    def test_data_loading_task(self):
        task = self.dag.get_task('load_and_process_data')
        self.assertEqual(task.python_callable.__name__, 'run_data_loading')

    @patch('SQLAlchemy_functions.start_session')
    @patch('data_loader.load_and_process_data_from_csv')
    def test_run_data_loading(self, mock_load_and_process_data, mock_start_session):
        mock_session = MagicMock()
        mock_start_session.return_value = mock_session

        run_data_loading()

        mock_start_session.assert_called_once_with('./config.json')
        mock_load_and_process_data.assert_called_once_with(
            csv_file_path='/home/ageq/Git_Projects/MLdatalake/source/combined.csv',
            session=mock_session,
            chunksize=100000,
        )
        mock_session.close.assert_called_once()

    @patch('zip_to_db_dag.main_extract_zip')
    def test_extract_zip_task_execution(self, mock_main_extract_zip):
        task = self.dag.get_task('extract_zip')
        context = {}
        task.execute(context)
        mock_main_extract_zip.assert_called_once_with(config_path='./config.json', source_path='/home/ageq/Git_Projects/MLdatalake/source')

    @patch('zip_to_db_dag.main_convert_csv')
    def test_convert_csv_task_execution(self, mock_main_convert_csv):
        task = self.dag.get_task('convert_csv_files')
        context = {}
        task.execute(context)
        mock_main_convert_csv.assert_called_once_with(extract_to_path='/home/ageq/Git_Projects/MLdatalake/source/archive', output_csv_path='/home/ageq/Git_Projects/MLdatalake/source/combined.csv')

    @patch('zip_to_db_dag.run_data_loading')
    def test_data_loading_task_execution(self, mock_run_data_loading):
        task = self.dag.get_task('load_and_process_data')
        context = {}
        task.execute(context)
        mock_run_data_loading.assert_called_once()

if __name__ == '__main__':
    unittest.main()
        mock_session.close.assert_called_once()

    @patch('zip_to_db_dag.main_extract_zip')
    def test_extract_zip_task_execution(self, mock_main_extract_zip):
        task = self.dag.get_task('extract_zip')
        context = {}
        task.execute(context)
        mock_main_extract_zip.assert_called_once_with(config_path='./config.json', source_path='/home/ageq/Git_Projects/MLdatalake/source')

    @patch('zip_to_db_dag.main_convert_csv')
    def test_convert_csv_task_execution(self, mock_main_convert_csv):
        task = self.dag.get_task('convert_csv_files')
        context = {}
        task.execute(context)
        mock_main_convert_csv.assert_called_once_with(extract_to_path='/home/ageq/Git_Projects/MLdatalake/source/archive', output_csv_path='/home/ageq/Git_Projects/MLdatalake/source/combined.csv')

if __name__ == '__main__':
    unittest.main()
