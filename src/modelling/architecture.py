"""Module architecture.py"""
import os

import transformers
import ray.train.huggingface.transformers as rt

import src.elements.variable as vr
import src.modelling.intelligence
import src.modelling.metrics
import src.modelling.parameters


class Architecture:
    """
    https://huggingface.co/docs/transformers/v4.44.0/en/main_classes/trainer#transformers.Seq2SeqTrainingArguments
    Hyperparameters, etc.: learning rate, weight decay, the batch sizes, number of training epochs
    """

    def __init__(self):
        """
        Constructor
        """

    @staticmethod
    def exc(config: dict):

        variable = vr.Variable()
        parameters = src.modelling.parameters.Parameters().parameters

        args: transformers.Seq2SeqTrainingArguments = transformers.Seq2SeqTrainingArguments(
            output_dir=variable.MODEL_OUTPUT_DIRECTORY,
            do_train=True,
            do_eval=True,
            eval_strategy='epoch',
            save_strategy='epoch',
            logging_strategy='epoch',
            learning_rate=config.get('learning_rate'),
            weight_decay=config.get('weight_decay'),
            per_device_train_batch_size=config.get('per_device_train_batch_size'),
            per_device_eval_batch_size=variable.VALIDATE_BATCH_SIZE,
            num_train_epochs=variable.EPOCHS,
            max_steps=config.get('max_steps'),
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

        # Directives
        metrics = src.modelling.metrics.Metrics(parameters=parameters)
        intelligence = src.modelling.intelligence.Intelligence(parameters=parameters)

        # Trainer
        trainer = transformers.Seq2SeqTrainer(
            model_init=intelligence.model, args=args,
            train_dataset=intelligence.iterable(segment='train', batch_size=variable.TRAIN_BATCH_SIZE),
            eval_dataset=intelligence.iterable(segment='eval', batch_size=variable.VALIDATE_BATCH_SIZE),
            tokenizer=parameters.tokenizer,
            data_collator=intelligence.collator(),
            compute_metrics=metrics.exc
        )
        trainer.add_callback(rt.RayTrainReportCallback())
        trainer = rt.prepare_trainer(trainer)

        return trainer.train()
