from data_cleaning_functions import *
from nlp import *
from tensorflow.keras.models import load_model


def main():
    # import json data into raw dataframe
    json_to_pickle('data_raw.pkl')
    # fix dataframe to be more dataframe-y
    data = clean_data(input_file='data_raw.pkl', output_file='data.pkl', printouts=True)

    # get chat names
    chatnames_df = get_chat_names('data.pkl', to_file=True)

    # create column containing lengths of chatnames
    chatnames_df['text_length'] = [len(message) for message in chatnames_df['chatname']]
    # chatnames_df['text_length'].plot(kind='hist', bins=30)
    # filter out group names with length > 120
    chatnames_df = chatnames_df[chatnames_df['text_length'] < 120]

    # add start and end tokens to input and output
    start_token = '\t'
    end_token = '\n'
    chatnames_df['inputs'], chatnames_df['targets'] = start_and_end_tokens(chatnames_df['chatname'],
                                                                           start_token=start_token,
                                                                           end_token=end_token)

    # build vocabulary
    vocab = build_vocabulary(chatnames_df['chatname'], start_token=start_token, end_token=end_token)
    print(f'vocabulary list: {sorted(list(vocab))}')
    print(f'vocabulary size: {len(vocab)}')

    with open('vocab.pkl', 'wb') as f:
        pickle.dump(vocab, f)

    # build character-to-index dictionaries for vectorisation
    char_to_idx, idx_to_char = char_to_int_maps(vocab)
    inputs, targets = gen_input_and_target(chatnames_df['inputs'], chatnames_df['targets'],
                                           vocab=vocab,
                                           seq_length=20,
                                           char_to_idx=char_to_idx,
                                           pickle_filename='tf_dataset.pkl')

    # generate model
    model = generate_model(vocab, rnn_units=128, seq_len=20)
    model = fit_model(model, inputs, targets)
    # model = load_model('model.h5')
    generate_text(model, n=10, max_len=120, seq_len=20, vocab=vocab,
                  char_to_idx=char_to_idx, idx_to_char=idx_to_char)


if __name__ == '__main__':
    main()
