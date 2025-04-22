import unittest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import sys

sys.modules['airflow'] = MagicMock()
sys.modules['airflow.DAG'] = MagicMock()
sys.modules['airflow.operators.python'] = MagicMock()
sys.modules['modules'] = MagicMock()
sys.modules['modules.SQLAlchemy_functions'] = MagicMock()
sys.modules['modules.Grabber'] = MagicMock()
sys.modules['modules.Grabber.grabber_load'] = MagicMock()

from dags.run.Grabber_dag import check_csv, load_and_process_assets, csv_file_path, config_file, dag, check_csv_task, load_assets_task

sys.modules['dags.run.Grabber_dag'] = MagicMock()

class TestGrabberDag(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("pandas.read_csv")
    def test_check_csv_empty_file(self, mock_read_csv, mock_open):
        check_csv(csv_file_path)
        mock_read_csv.assert_called_once_with(csv_file_path)
        mock_open.assert_called_once_with(csv_file_path, 'r')

    @patch("builtins.open", new_callable=mock_open, read_data="ticker\nAAPL\nGOOGL")
    @patch("pandas.read_csv")
    def test_check_csv_non_empty_file(self, mock_read_csv, mock_open):
        check_csv(csv_file_path)
        mock_read_csv.assert_called_once_with(csv_file_path)
        mock_open.assert_called_once_with(csv_file_path, 'r')

    @patch("pandas.read_csv")
    @patch("modules.SQLAlchemy_functions.start_session")
    @patch("modules.Grabber.grabber_load.process_asset")
    def test_load_and_process_assets(self, mock_process_asset, mock_start_session, mock_read_csv):
        mock_session = MagicMock()
        mock_start_session.return_value = mock_session
        mock_read_csv.return_value = pd.DataFrame({'ticker': ['AAPL', 'GOOGL']})

        load_and_process_assets(config_file, csv_file_path)
        
        print(f"Aufrufe von start_session: {mock_start_session.call_args_list}")

        mock_start_session.assert_called_once_with(config_file)

    @patch("airflow.DAG")
    @patch("airflow.operators.python.PythonOperator")
    def test_dag_creation(self, mock_python_operator, mock_dag):
        from dags.run.Grabber_dag import dag, check_csv_task, load_assets_task

        mock_dag.assert_called_once_with('Grabber', default_args=unittest.mock.ANY, schedule_interval='@daily')
        mock_python_operator.assert_any_call(
            task_id='check_csv',
            python_callable=check_csv,
            op_args=[csv_file_path]
        )
        mock_python_operator.assert_any_call(
            task_id='load_and_process_assets',
            python_callable=load_and_process_assets,
            op_args=[config_file, csv_file_path]
        )
        self.assertEqual(check_csv_task >> load_assets_task, unittest.mock.ANY)

if __name__ == "__main__":
    unittest.main()