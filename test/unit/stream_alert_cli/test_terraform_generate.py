'''
Copyright 2017-present, Airbnb Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import base64
import json

from nose.tools import assert_equal, assert_not_equal

from stream_alert_cli import terraform_generate


class TestTerraformGenerate(object):
    """Test class for the Terraform Cluster Generating"""

    @classmethod
    def setup_class(cls):
        """Setup the class before any methods"""
        cls.env = {
            'lambda_region': 'us-east-1',
            'account_id': '123456789012',
            'lambda_function_name': 'test_kinesis_stream',
            'lambda_alias': 'production'
        }

    @classmethod
    def teardown_class(cls):
        """Teardown the class after all methods"""
        cls.env = None

    def setup(self):
        """Setup before each method"""
        self.base_config = {
            'global': {
                'account': {
                    'prefix': 'unit-testing',
                    'kms_key_alias': 'unit-testing'
                },
                'terraform': {
                    'tfstate_bucket': 'unit-testing.terraform.tfstate'
                }
            },
            'lambda': {
                'rule_processor_config': {
                    'source_bucket': 'unit.testing.source.bucket'
                }
            }
        }

    def teardown(self):
        """Teardown after each method"""

    def test_generate_s3_bucket(self):
        """CLI - Terraform Generate S3 Bucket """
        bucket = terraform_generate.generate_s3_bucket(
            bucket='unit.test.bucket',
            logging='my.s3-logging.bucket',
            force_destroy=True
        )

        required_keys = {
            'bucket',
            'acl',
            'force_destroy',
            'versioning',
            'logging'
        }

        assert_equal(type(bucket), dict)
        assert_equal(bucket['bucket'], 'unit.test.bucket')
        assert_equal(set(bucket.keys()), required_keys)

    def test_generate_s3_bucket_lifecycle(self):
        """CLI - Terraform Generate S3 Bucket with Lifecycle"""
        bucket = terraform_generate.generate_s3_bucket(
            bucket='unit.test.bucket',
            logging='my.s3-logging.bucket',
            force_destroy=False,
            lifecycle_rule={
                'prefix': 'logs/',
                'enabled': True,
                'transition': {'days': 30, 'storage_class': 'GLACIER'}
            }
        )

        assert_equal(bucket['lifecycle_rule']['prefix'], 'logs/')
        assert_equal(bucket['force_destroy'], False)
        assert_equal(type(bucket['lifecycle_rule']), dict)
        assert_equal(type(bucket['versioning']), dict)

    def test_generate_main(self):
        """CLI - Terraform Generate Main"""
        init = False
        config = self.base_config

        tf_main = terraform_generate.generate_main(
            config=config,
            init=init
        )

        main_keys = {
            'provider',
            'terraform',
            'resource'
        }
        main_buckets = {
            'lambda_source',
            'stream_alert_secrets',
            'terraform_remote_state',
            'logging_bucket'
        }
        main_resources = {
            'aws_kms_key',
            'aws_kms_alias',
            'aws_s3_bucket'
        }

        assert_equal('s3' in tf_main['terraform']['backend'], True)
        assert_equal(set(tf_main.keys()), main_keys)
        assert_equal(set(tf_main['resource']['aws_s3_bucket'].keys()), main_buckets)
        assert_equal(set(tf_main['resource'].keys()), main_resources)

    def test_generate_stream_alert(self):
        """CLI - Terraform Generate Stream_Alert Module"""
        pass

    def test_generate_cluster(self):
        """CLI - Terraform Generate Cluster"""
        pass