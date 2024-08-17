"""Module architecture.py"""
import os
import transformers

import ray.train.huggingface.transformers as rt

import src.modelling.t5.metrics
import src.modelling.t5.intelligence

import src.modelling.t5.custom
import src.modelling.t5.parameters as pr


class Architecture:
    """
    https://huggingface.co/docs/transformers/v4.44.0/en/main_classes/trainer#transformers.Seq2SeqTrainingArguments
    Hyperparameters, etc.: learning rate, weight decay, the batch sizes, number of training epochs
    """

    def __init__(self):
        pass

    @staticmethod
    def exc(config: dict):
        """
        https://huggingface.co/docs/transformers/main_classes/trainer#transformers.Seq2SeqTrainer

        :param config:
        :return:
        """

        variable = src.modelling.t5.custom.Custom().custom
        parameters = pr.Parameters()

        metrics = src.modelling.t5.metrics.Metrics()
        intelligence = src.modelling.t5.intelligence.Intelligence()

        args: transformers.Seq2SeqTrainingArguments = transformers.Seq2SeqTrainingArguments(
            output_dir=variable.MODEL_OUTPUT_DIRECTORY,
            do_train=True,
            do_eval=True,
            eval_strategy='epoch',
            save_strategy='epoch',
            logging_strategy='epoch',
            learning_rate=variable.LEARNING_RATE,
            weight_decay=config.get('weight_decay'),
            per_device_train_batch_size=config.get('per_device_train_batch_size'),
            per_device_eval_batch_size=variable.VALIDATE_BATCH_SIZE,
            num_train_epochs=variable.EPOCHS,
            max_steps=variable.MAX_STEPS,
            warmup_steps=0,
            logging_dir=os.path.join(variable.MODEL_OUTPUT_DIRECTORY, '.logs'),
            no_cuda=False,
            seed=5,
            save_total_limit=2,
            skip_memory_metrics=True,
            load_best_model_at_end=True,
            predict_with_generate=True,
            fp16=True,
            push_to_hub=False
        )

        trainer = transformers.Seq2SeqTrainer(
            model_init=intelligence.model,
            args=args,
            train_dataset=intelligence.iterable(segment='train', batch_size=variable.TRAIN_BATCH_SIZE),
            eval_dataset=intelligence.iterable(segment='eval', batch_size=variable.VALIDATE_BATCH_SIZE),
            tokenizer=parameters.tokenizer,
            data_collator=intelligence.data_collator(),
            compute_metrics=metrics.exc
        )
        trainer.add_callback(rt.RayTrainReportCallback())
        trainer = rt.prepare_trainer(trainer)
        trainer.train()