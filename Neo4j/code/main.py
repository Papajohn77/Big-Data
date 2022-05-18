import os
from dotenv import load_dotenv
from neo4j import GraphDatabase


def get_driver():
    load_dotenv() # Parses a .env file and loads the environment variables.
    scheme = os.getenv('SCHEME')
    host_name = os.getenv('HOST_NAME')
    port = os.getenv('PORT')
    uri = f"{scheme}://{host_name}:{port}"
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    return GraphDatabase.driver(uri, auth=(user, password))


def create_user(tx, user_id):
    tx.run("MERGE (u:User { user_id: $user_id })", user_id=user_id)


def create_target(tx, target_id):
    tx.run("MERGE (t:Target { target_id: $target_id })", target_id=target_id)


def create_action(tx, user_id, target_id, action_id, timestamp,
        feature_0, feature_1, feature_2, feature_3, label):
    tx.run("MATCH (u:User { user_id: $user_id }), (t:Target { target_id: $target_id }) "
           "CREATE (u) -[:Action { action_id: $action_id, timestamp: $timestamp, "
           "feature_0: $feature_0, feature_1: $feature_1, feature_2: $feature_2, "
           "feature_3: $feature_3, label: $label }]-> (t)",
           user_id=user_id, target_id=target_id, action_id=action_id, timestamp=timestamp,
           feature_0=feature_0, feature_1=feature_1, feature_2=feature_2,
           feature_3=feature_3, label=label)


if __name__ == "__main__":
    driver = get_driver()

    with open('../data/mooc_actions.tsv') as actions_f, \
            open('../data/mooc_action_features.tsv') as features_f, \
            open('../data/mooc_action_labels.tsv') as labels_f, \
            driver.session() as session:
        next(actions_f) # Skips the 1st line containing the column labels.
        next(features_f) # Skips the 1st line containing the column labels.
        next(labels_f) # Skips the 1st line containing the column labels.

        for line_1, line_2, line_3 in zip(actions_f, features_f, labels_f):
            line_1_elements = line_1.strip().split('\t')
            timestamp = float(line_1_elements[-1])
            action_id, user_id, target_id = [int(e) for e in line_1_elements[:-1]]

            line_2_elements = line_2.strip().split('\t')
            feature_0, feature_1, feature_2, feature_3 = \
                [float(e) for e in line_2_elements[1:]]

            line_3_elements = line_3.strip().split('\t')
            label = int(line_3_elements[-1])

            session.write_transaction(create_user, user_id)
            session.write_transaction(create_target, target_id)
            session.write_transaction(create_action, user_id, target_id, action_id, timestamp,
                feature_0, feature_1, feature_2, feature_3, label)

    driver.close()
