from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from . import search
from . import utils

import os
import requests
import json
import logging


# replace after you deploy your llm (deploy_llm.py)
LLM_HOST = ""
LLM_PORT = ""

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ActionParseContract(Action):
    metadata_dir = "../contract/file/storage/plain_text"
    def name(self) -> str:
        return "action_parse_contract"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        contract_id = next(tracker.get_latest_entity_values('contract_id'), None)
        if contract_id:
            dispatcher.utter_message(text=f"Получили договор с ID: {contract_id}. Что вы хотите в нём изменить?")
            contract_metadata = utils.read_json(os.path.join(self.metadata_dir, f'{contract_id}.json'))
            logger.info(contract_metadata)
            return [
                SlotSet("contract_id", contract_id), 
                SlotSet("contract_metadata", json.dumps(contract_metadata))
            ]
        dispatcher.utter_message(text="Не удалось распознать идентификатор договора.")
        return []

class ActionHandleReason(Action):
    directory_path = "../data/rag/files"

    def name(self) -> str:
        return "action_handle_reason"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        reason = next(tracker.get_latest_entity_values('reason'), None)
        
        logger.info(reason)

        current_state = tracker.current_state()
        latest_message = current_state["latest_message"]["text"]

        logger.info(latest_message)

        if reason:
            logger.info("Found reason")
            dispatcher.utter_message(text=f"Распознанная причина изменения договора: {reason}.")

            search_results = search.search_in_index_3(reason)

            logger.info("search results")

            if len(search_results) == 0: # TODO: add rag
                search_results = [""]

            context = ""
            
            for search_result in search_results[:3]:
                context += utils.read_file(os.path.join(self.directory_path, search_result)) + "\n\n"

            final_prompt = utils.prompt.format(search_query=latest_message, context=context)

            logger.info(f"prompt: {str(final_prompt)}")
            
            payload = {
                "prompt": final_prompt
            }

            # Make the POST request
            response = requests.post(f"http://{LLM_HOST}:{LLM_PORT}/request", json=payload)

            logger.info("llm")

            try:
                dispatcher.utter_message(text=f"{response.json()['result']}")
            except Exception as e:
                logger.error(str(e))
                logger.error(response.text)
                dispatcher.utter_message(text="Возникла внутренняя ошибка, попробуйте обновить страницу.")

            dispatcher.utter_message(text="На основании предоставленной информации, хотите ли вы создать доп.соглашение?")

            logger.info("end")
            # Implement your actual handling logic here
            return [SlotSet("reason", reason)]
        return []

class ActionGenerateAdditionalAgreement(Action):

    def name(self) -> str:
        return "action_generate_additional_agreement"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Implement your logic to generate additional agreement here
        dispatcher.utter_message(text="Generating the additional agreement based on the provided reason and contract.")
        # Assume a file generation happens here
        additional_agreement_file = "/path/to/additional_agreement.pdf"
        dispatcher.utter_message(text=f"The additional agreement has been generated: {additional_agreement_file}")
        return []


class ActionSendAgreementMetadata(Action):

    def name(self) -> str:
        return "action_send_agreement_metadata"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Implement your logic to generate additional agreement here
        # dispatcher.utter_message(text="{'text': 'Ваша ссылка на скачивание: ', 'file_path': '/Users/mikhail/tenderhack/tender_front/static/docs/additional_template.docx', 'sender': session_id, 'context': {'contract_date': '2012-22-12', 'contract_number': 123, 'customer_name': 'Александр Перелов', 'customer_agent': 'Мущинский', 'customer_agent_name': 'Сергэй БобкоФФ', 'customer_act': 'Акт об показывании мущинского', 'supplier_name': 'Газпром нефть', 'supplier_agent_name': 'Суперагент', 'supplier_act': 'Акт в массажный салон 109'}}")
        logger.info("Entering action_send_agreement_metadata")
        dispatcher.utter_message(text="На основе введённой информации мы предлагаем следующее доп. соглашение.")
        contract_metadata = tracker.get_slot("contract_metadata")
        logger.info(contract_metadata)
        dispatcher.utter_message(text=contract_metadata)
        dispatcher.utter_message(text="Проверьте дополнительное соглашение, если вы хотите что-то поменять, то просто напишите вносимые изменения")
        return []

class ActionHandleProposedChanges(Action):

    def name(self) -> str:
        return "action_handle_proposed_changes"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Implement your logic to generate additional agreement here
        # dispatcher.utter_message(text="{'text': 'Ваша ссылка на скачивание: ', 'file_path': '/Users/mikhail/tenderhack/tender_front/static/docs/additional_template.docx', 'sender': session_id, 'context': {'contract_date': '2012-22-12', 'contract_number': 123, 'customer_name': 'Александр Перелов', 'customer_agent': 'Мущинский', 'customer_agent_name': 'Сергэй БобкоФФ', 'customer_act': 'Акт об показывании мущинского', 'supplier_name': 'Газпром нефть', 'supplier_agent_name': 'Суперагент', 'supplier_act': 'Акт в массажный салон 109'}}")
        current_state = tracker.current_state()
        details = current_state["latest_message"]["text"]
        
        final_prompt = utils.details_prompt.format(details=details) # TODO: add reason?

        payload = {
            "prompt": final_prompt
        }

        # Make the POST request
        response = requests.post(f"http://{LLM_HOST}:{LLM_PORT}/request", json=payload)

        main_reason = ""

        try:
            main_reason = response.json()['result']
            logger.info(main_reason)
            dispatcher.utter_message(text=f"{main_reason}")
        except Exception as e:
            logger.error(str(e))
            logger.error(response.text)
            dispatcher.utter_message(text="Возникла внутренняя ошибка, попробуйте обновить страницу.")

        try:
            contract_metadata = json.loads(tracker.get_slot("contract_metadata"))
            contract_metadata["reason_contract_change"] = main_reason
        except Exception as e:
            logger.error(str(e))
            logger.error(response.text)
            dispatcher.utter_message(text="Возникла внутренняя ошибка, попробуйте обновить страницу.")

        return [SlotSet("contract_metadata", json.dumps(contract_metadata)), SlotSet("proposed_changes", main_reason)]

    class ActionChangeExistingAgreement(Action):

        def name(self) -> str:
            return "action_change_existing_agreement"

        def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
            # Implement your logic to generate additional agreement here
            logger.info("Entering action_change_existing_agreement")

            current_state = tracker.current_state()
            new_changes = current_state["latest_message"]["text"]

            proposed_changes = tracker.get_slot("proposed_changes")

            final_prompt = utils.change_prompt.format(proposed_changes=proposed_changes, new_changes=new_changes)

            payload = {
                "prompt": final_prompt
            }

            # Make the POST request
            response = requests.post(f"http://{LLM_HOST}:{LLM_PORT}/request", json=payload)

            main_reason = ""

            try:
                main_reason = response.json()['result']
                logger.info(main_reason)
                dispatcher.utter_message(text=f"{main_reason}")
            except Exception as e:
                logger.error(str(e))
                logger.error(response.text)
                dispatcher.utter_message(text="Возникла внутренняя ошибка, попробуйте обновить страницу.")

            try:
                contract_metadata = json.loads(tracker.get_slot("contract_metadata"))
                contract_metadata["reason_contract_change"] = main_reason
            except Exception as e:
                logger.error(str(e))
                logger.error(response.text)
                dispatcher.utter_message(text="Возникла внутренняя ошибка, попробуйте обновить страницу.")

            return []