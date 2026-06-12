# Backend

The backend implements the RAG model and an API to communicate with it. The rest of this README covers how to run and [configure](#configuration) the backend. There is a [development document](./development.md) that covers the structure and development tools of the RAG.

## [Configuration](./config.yaml)

The configuration file is used to configure [pathing](#paths) within the backend, [hosting](#apitodo) the API, and the underlying [embedding](#embeddingtodo)/[LLM](#llm) models. A default one is provided.

### Paths

There are three paths that matter. The first is the location of the [repo list](#repositories-list). The second is the directory to clone the repos into. The third one is the directory associated with the database. The final one is the file to set [environment variables](#environment-variables). The paths are **relative to the backend directory**.

#### Repositories List

```txt
https://github.com/KhuramC/KrumCode
https://github.com/git/git.git
```

Above is a valid example of the repository list, the list of repos the RAG will reference. The repo list is a TXT file of URLs that one can clone. Each line is a different URL. One needs to ensure they have access to the repository. For example, with private GitHub repositories, one needs put down the SSH URL and have an associated GitHub private key.

### API

The API is pretty simple. The host is the IP address, the port is self-explanatory, and development changes things for production vs development.

### Logging

Logging is pretty simple. Each main part of the project (the API, the RAG, and the utilities) has its own levels of logging, based on the standard logging levels. Timestamps can be on there, but they don't need to be.

### Embedding(TODO)

### LLM

There are two options to do with the LLM. The first is the provider, such as OpenAI. The second is the actual LLM model being used.

#### Environment Variables

```bash
LLM_API_KEY=API_KEY_TO_DESIRED_LLM
```

If the provider is not local, an API key is required to interface with the LLM. This can be set in the `.env` file as shown in the example above.
