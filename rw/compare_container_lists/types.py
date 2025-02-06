from .readers import ContainerReader, Container8Reader

VAGONS = 'vagons'
CONTAINERS = 'containers'


reader_types = {
    VAGONS: Container8Reader,
    CONTAINERS: ContainerReader
}
